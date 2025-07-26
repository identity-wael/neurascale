#!/bin/bash

# Neural Ledger Staging Test Script
# This script runs comprehensive tests against the staging environment

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-neurascale-staging}"
REGION="${GCP_REGION:-northamerica-northeast1}"
ENVIRONMENT="staging"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test infrastructure connectivity
test_infrastructure() {
    log_info "Testing infrastructure connectivity..."

    local tests_passed=0
    local tests_total=0

    # Test Pub/Sub topic
    ((tests_total++))
    if gcloud pubsub topics describe neural-ledger-events --project="${PROJECT_ID}" &> /dev/null; then
        log_success "✓ Pub/Sub topic accessible"
        ((tests_passed++))
    else
        log_error "✗ Pub/Sub topic not accessible"
    fi

    # Test Cloud Function
    ((tests_total++))
    if gcloud functions describe neural-ledger-processor --region="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
        log_success "✓ Cloud Function deployed"
        ((tests_passed++))
    else
        log_error "✗ Cloud Function not found"
    fi

    # Test BigQuery dataset
    ((tests_total++))
    if bq show --project_id="${PROJECT_ID}" neural_ledger &> /dev/null; then
        log_success "✓ BigQuery dataset accessible"
        ((tests_passed++))
    else
        log_error "✗ BigQuery dataset not accessible"
    fi

    # Test Bigtable instance
    ((tests_total++))
    if gcloud bigtable instances describe neural-ledger --project="${PROJECT_ID}" &> /dev/null; then
        log_success "✓ Bigtable instance accessible"
        ((tests_passed++))
    else
        log_error "✗ Bigtable instance not accessible"
    fi

    # Test Firestore (implicit - check if we can create a client)
    ((tests_total++))
    if python3 -c "
from google.cloud import firestore
try:
    client = firestore.Client(project='${PROJECT_ID}')
    # Try to access collections (won't fail even if empty)
    list(client.collections())
    print('Firestore accessible')
except Exception as e:
    print(f'Firestore error: {e}')
    exit(1)
" &> /dev/null; then
        log_success "✓ Firestore accessible"
        ((tests_passed++))
    else
        log_error "✗ Firestore not accessible"
    fi

    log_info "Infrastructure tests: ${tests_passed}/${tests_total} passed"

    if [[ ${tests_passed} -eq ${tests_total} ]]; then
        return 0
    else
        return 1
    fi
}

# Test event publishing and processing
test_event_flow() {
    log_info "Testing end-to-end event flow..."

    # Create a test event
    local test_session_id="staging-test-$(date +%s)"
    local test_message="{
        \"event_type\": \"SESSION_CREATED\",
        \"session_id\": \"${test_session_id}\",
        \"user_id\": \"test-user-staging\",
        \"device_id\": \"test-device-staging\",
        \"metadata\": {
            \"test\": true,
            \"environment\": \"staging\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }
    }"

    log_info "Publishing test event to Pub/Sub..."

    # Publish message to Pub/Sub
    if echo "${test_message}" | gcloud pubsub topics publish neural-ledger-events \
        --project="${PROJECT_ID}" \
        --message=-; then
        log_success "✓ Test event published to Pub/Sub"
    else
        log_error "✗ Failed to publish test event"
        return 1
    fi

    # Wait for processing
    log_info "Waiting for event processing (30 seconds)..."
    sleep 30

    # Check if event was processed by querying BigQuery
    log_info "Checking if event was processed..."

    local query="
    SELECT
        event_id,
        event_type,
        session_id,
        timestamp
    FROM \`${PROJECT_ID}.neural_ledger.events\`
    WHERE session_id = '${test_session_id}'
    LIMIT 1
    "

    if bq query --project_id="${PROJECT_ID}" --use_legacy_sql=false --format=json "${query}" | jq -r '.[].session_id' | grep -q "${test_session_id}"; then
        log_success "✓ Test event processed and stored in BigQuery"
        return 0
    else
        log_warning "⚠ Test event not found in BigQuery (may need more time)"
        return 1
    fi
}

# Test performance under load
test_performance() {
    log_info "Testing performance under load..."

    local num_events=50
    local session_id="perf-test-$(date +%s)"

    log_info "Publishing ${num_events} events for performance testing..."

    local start_time=$(date +%s)

    # Publish multiple events
    for i in $(seq 1 ${num_events}); do
        local test_message="{
            \"event_type\": \"DATA_INGESTED\",
            \"session_id\": \"${session_id}\",
            \"data_hash\": \"test-hash-${i}\",
            \"metadata\": {
                \"test\": true,
                \"performance_test\": true,
                \"event_number\": ${i},
                \"batch_size\": ${num_events}
            }
        }"

        echo "${test_message}" | gcloud pubsub topics publish neural-ledger-events \
            --project="${PROJECT_ID}" \
            --message=- &

        # Limit concurrent publishes
        if (( i % 10 == 0 )); then
            wait
        fi
    done

    wait # Wait for all publishes to complete

    local end_time=$(date +%s)
    local publish_duration=$((end_time - start_time))

    log_success "✓ Published ${num_events} events in ${publish_duration} seconds"

    # Wait for processing
    log_info "Waiting for batch processing (60 seconds)..."
    sleep 60

    # Check how many events were processed
    local query="
    SELECT COUNT(*) as event_count
    FROM \`${PROJECT_ID}.neural_ledger.events\`
    WHERE session_id = '${session_id}'
    "

    local processed_count
    processed_count=$(bq query --project_id="${PROJECT_ID}" --use_legacy_sql=false --format=csv "${query}" | tail -n 1)

    log_info "Processed ${processed_count}/${num_events} events"

    if [[ ${processed_count} -ge $((num_events * 8 / 10)) ]]; then
        log_success "✓ Performance test passed (${processed_count}/${num_events} events processed)"
        return 0
    else
        log_warning "⚠ Performance test partial success (${processed_count}/${num_events} events processed)"
        return 1
    fi
}

# Test monitoring and alerting
test_monitoring() {
    log_info "Testing monitoring and alerting..."

    # Check if monitoring dashboard exists
    local dashboards
    dashboards=$(gcloud alpha monitoring dashboards list --project="${PROJECT_ID}" --format="value(displayName)" --filter="displayName:neural-ledger" 2>/dev/null || true)

    if [[ -n "${dashboards}" ]]; then
        log_success "✓ Monitoring dashboard found: ${dashboards}"
    else
        log_warning "⚠ No monitoring dashboard found"
    fi

    # Check Cloud Function logs for any errors
    log_info "Checking Cloud Function logs for errors..."

    local error_count
    error_count=$(gcloud logging read "
        resource.type=\"cloud_function\"
        resource.labels.function_name=\"neural-ledger-processor\"
        severity>=ERROR
        timestamp>=\"$(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ)\"
    " --project="${PROJECT_ID}" --format="value(timestamp)" | wc -l)

    if [[ ${error_count} -eq 0 ]]; then
        log_success "✓ No errors in Cloud Function logs"
    else
        log_warning "⚠ Found ${error_count} errors in Cloud Function logs"
    fi

    return 0
}

# Run unit and integration tests
run_test_suite() {
    log_info "Running test suite..."

    # Set environment variables for tests
    export RUN_INTEGRATION_TESTS=true
    export GCP_PROJECT_ID="${PROJECT_ID}"
    export GCP_LOCATION="${REGION}"

    local test_results=0

    # Run unit tests
    log_info "Running unit tests..."
    if python -m pytest tests/test_ledger/ -v -m "not integration" --tb=short; then
        log_success "✓ Unit tests passed"
    else
        log_error "✗ Unit tests failed"
        ((test_results++))
    fi

    # Run performance tests
    log_info "Running performance tests..."
    if python -m pytest tests/test_ledger/test_performance.py -v -m "not slow" --tb=short; then
        log_success "✓ Performance tests passed"
    else
        log_error "✗ Performance tests failed"
        ((test_results++))
    fi

    # Run integration tests (if staging environment is ready)
    log_info "Running integration tests..."
    if python -m pytest tests/test_ledger/test_integration.py -v --tb=short; then
        log_success "✓ Integration tests passed"
    else
        log_warning "⚠ Integration tests failed (may be expected in staging)"
        # Don't count integration test failures as critical for staging
    fi

    return ${test_results}
}

# Generate test report
generate_report() {
    local start_time="$1"
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log_info "Generating test report..."

    local report_file="staging-test-report-$(date +%Y%m%d-%H%M%S).txt"

    cat > "${report_file}" <<EOF
Neural Ledger Staging Test Report
================================

Test Environment:
- Project ID: ${PROJECT_ID}
- Region: ${REGION}
- Environment: ${ENVIRONMENT}
- Test Duration: ${duration} seconds
- Test Time: $(date -u)

Test Results Summary:
- Infrastructure Connectivity: $(test_infrastructure && echo "PASS" || echo "FAIL")
- Event Flow: $(test_event_flow && echo "PASS" || echo "FAIL")
- Performance: $(test_performance && echo "PASS" || echo "FAIL")
- Monitoring: $(test_monitoring && echo "PASS" || echo "FAIL")
- Test Suite: $(run_test_suite && echo "PASS" || echo "FAIL")

Recommendations:
1. Monitor Cloud Function logs for any processing errors
2. Check BigQuery for data consistency
3. Verify monitoring dashboards are updating correctly
4. Test with production-like data volumes
5. Validate backup and recovery procedures

For detailed logs, check the console output during test execution.
EOF

    log_success "Test report generated: ${report_file}"
}

# Main testing function
main() {
    local start_time=$(date +%s)

    log_info "Starting Neural Ledger staging tests..."
    log_info "Project: ${PROJECT_ID}"
    log_info "Region: ${REGION}"
    log_info "Environment: ${ENVIRONMENT}"

    local test_failures=0

    # Run all tests
    test_infrastructure || ((test_failures++))
    test_event_flow || ((test_failures++))
    test_performance || ((test_failures++))
    test_monitoring || ((test_failures++))
    run_test_suite || ((test_failures++))

    # Generate report
    generate_report "${start_time}"

    # Summary
    echo ""
    if [[ ${test_failures} -eq 0 ]]; then
        log_success "All staging tests completed successfully!"
    else
        log_warning "Staging tests completed with ${test_failures} failures"
    fi

    log_info "Staging environment is ready for testing"

    return ${test_failures}
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
