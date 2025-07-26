#!/bin/bash

# Monitor Neural Engine CI/CD Pipeline
echo "Neural Engine CI/CD Pipeline Monitor"
echo "===================================="
echo ""

# Function to format time
format_time() {
    local seconds=$1
    if [ $seconds -lt 60 ]; then
        echo "${seconds}s"
    elif [ $seconds -lt 3600 ]; then
        echo "$((seconds / 60))m $((seconds % 60))s"
    else
        echo "$((seconds / 3600))h $((seconds % 3600 / 60))m"
    fi
}

# Get latest run
RUN_INFO=$(gh run list --repo identity-wael/neurascale --workflow neural-engine-cicd.yml --limit 1 --json databaseId,status,conclusion,startedAt,workflowName)
RUN_ID=$(echo "$RUN_INFO" | jq -r '.[0].databaseId')
RUN_STATUS=$(echo "$RUN_INFO" | jq -r '.[0].status')
RUN_CONCLUSION=$(echo "$RUN_INFO" | jq -r '.[0].conclusion // "in progress"')
RUN_STARTED=$(echo "$RUN_INFO" | jq -r '.[0].startedAt')

# Calculate elapsed time
if [ "$RUN_STARTED" != "null" ]; then
    START_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$RUN_STARTED" "+%s" 2>/dev/null || date -d "$RUN_STARTED" "+%s")
    NOW_EPOCH=$(date "+%s")
    ELAPSED=$((NOW_EPOCH - START_EPOCH))
    ELAPSED_STR=$(format_time $ELAPSED)
else
    ELAPSED_STR="N/A"
fi

echo "Latest Pipeline Run: #$RUN_ID"
echo "Status: $RUN_STATUS ($RUN_CONCLUSION)"
echo "Elapsed: $ELAPSED_STR"
echo ""

# Get job details
echo "Jobs:"
echo "-----"
gh api repos/identity-wael/neurascale/actions/runs/$RUN_ID/jobs --jq '.jobs[] |
    "\(.name): \(.status) - \(.conclusion // "running") [\(.runner_name // "queued")]"' |
    sed 's/^/  /'

echo ""
echo "Runners:"
echo "--------"
# Show runner status
gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] |
    "\(.name): \(.status) \(if .busy then "[BUSY]" else "[IDLE]" end)"' |
    sed 's/^/  /'

echo ""
echo "Active Jobs on Runners:"
echo "----------------------"
# Show what each runner is doing
for i in {1..6}; do
    if [ $i -eq 1 ]; then
        LOG_FILE="/Users/weg/actions-runner/runner.log"
    else
        LOG_FILE="/Users/weg/actions-runner-$i/runner.log"
    fi

    if [ -f "$LOG_FILE" ]; then
        CURRENT_JOB=$(tail -n 20 "$LOG_FILE" 2>/dev/null | grep -E "Running job:|Completed job:" | tail -1)
        if [ -n "$CURRENT_JOB" ]; then
            echo "  Runner $i: $CURRENT_JOB"
        fi
    fi
done

echo ""
echo "Refresh: cd scripts/runners && ./monitor-pipeline.sh"
echo "Watch: cd scripts/runners && watch -n 5 ./monitor-pipeline.sh"
