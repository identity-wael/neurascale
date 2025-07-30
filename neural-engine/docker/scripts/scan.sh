#!/bin/bash
# Security scanning script for Neural Engine Docker images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
SEVERITY="HIGH,CRITICAL"
FORMAT="table"
OUTPUT_DIR="./scan-results"
SCAN_ALL=false
EXIT_ON_VULNERABILITY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --severity)
            SEVERITY="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --all)
            SCAN_ALL=true
            shift
            ;;
        --exit-on-vulnerability)
            EXIT_ON_VULNERABILITY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --severity LEVEL     Severity levels (default: HIGH,CRITICAL)"
            echo "  --format FORMAT      Output format: table, json, sarif (default: table)"
            echo "  --output DIR         Output directory for results (default: ./scan-results)"
            echo "  --all                Scan all images including base images"
            echo "  --exit-on-vulnerability  Exit with error if vulnerabilities found"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Services to scan
SERVICES=(
    "neural-processor"
    "device-manager"
    "api-gateway"
    "ml-pipeline"
)

# Base images (if --all specified)
if [ "$SCAN_ALL" = true ]; then
    BASE_IMAGES=(
        "base:python"
        "base:golang"
        "base:node"
        "base:ml-base"
    )
else
    BASE_IMAGES=()
fi

echo -e "${GREEN}Scanning Neural Engine Docker images for vulnerabilities...${NC}"
echo "Severity: $SEVERITY"
echo "Format: $FORMAT"
echo "Output: $OUTPUT_DIR"

# Check if Trivy is installed
if ! command -v trivy &>/dev/null; then
    echo -e "${YELLOW}Trivy not found. Installing...${NC}"
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
fi

# Track vulnerability count
TOTAL_VULNERABILITIES=0
SCANNED_IMAGES=0
FAILED_SCANS=0

# Function to scan image
scan_image() {
    local image=$1
    local name=$(echo "$image" | tr '/:' '-')
    local output_file="$OUTPUT_DIR/${name}-scan"

    echo -e "${BLUE}Scanning $image...${NC}"

    # Run Trivy scan
    if trivy image \
        --severity "$SEVERITY" \
        --format "$FORMAT" \
        --output "${output_file}.${FORMAT}" \
        "neurascale/$image:latest" 2>/dev/null; then

        SCANNED_IMAGES=$((SCANNED_IMAGES + 1))

        # Also generate JSON for parsing
        if [ "$FORMAT" != "json" ]; then
            trivy image \
                --severity "$SEVERITY" \
                --format json \
                --output "${output_file}.json" \
                "neurascale/$image:latest" 2>/dev/null || true
        fi

        # Count vulnerabilities
        if [ -f "${output_file}.json" ]; then
            VULN_COUNT=$(jq '[.Results[].Vulnerabilities | length] | add // 0' "${output_file}.json")
            TOTAL_VULNERABILITIES=$((TOTAL_VULNERABILITIES + VULN_COUNT))

            if [ "$VULN_COUNT" -gt 0 ]; then
                echo -e "${RED}  Found $VULN_COUNT vulnerabilities${NC}"

                # Show summary
                jq -r '.Results[].Vulnerabilities[] | "\(.Severity): \(.VulnerabilityID) - \(.PkgName) \(.InstalledVersion)"' \
                    "${output_file}.json" | head -10

                if [ "$VULN_COUNT" -gt 10 ]; then
                    echo "  ... and $((VULN_COUNT - 10)) more"
                fi
            else
                echo -e "${GREEN}  No vulnerabilities found${NC}"
            fi
        fi
    else
        echo -e "${RED}  Scan failed${NC}"
        FAILED_SCANS=$((FAILED_SCANS + 1))
    fi

    echo ""
}

# Scan service images
for SERVICE in "${SERVICES[@]}"; do
    if docker image inspect "neurascale/$SERVICE:latest" &>/dev/null; then
        scan_image "$SERVICE"
    else
        echo -e "${YELLOW}Warning: Image not found: neurascale/$SERVICE:latest${NC}"
    fi
done

# Scan base images if requested
for BASE in "${BASE_IMAGES[@]}"; do
    if docker image inspect "neurascale/$BASE" &>/dev/null; then
        scan_image "$BASE"
    fi
done

# Generate summary report
SUMMARY_FILE="$OUTPUT_DIR/scan-summary.txt"
{
    echo "Neural Engine Security Scan Summary"
    echo "==================================="
    echo "Date: $(date)"
    echo "Scanned Images: $SCANNED_IMAGES"
    echo "Failed Scans: $FAILED_SCANS"
    echo "Total Vulnerabilities: $TOTAL_VULNERABILITIES"
    echo ""
    echo "Severity Filter: $SEVERITY"
    echo ""
    echo "Detailed reports available in: $OUTPUT_DIR"
} > "$SUMMARY_FILE"

echo -e "${GREEN}Scan complete!${NC}"
echo -e "Summary saved to: ${BLUE}$SUMMARY_FILE${NC}"
echo ""
cat "$SUMMARY_FILE"

# Generate SARIF report for GitHub integration if requested
if [ "$FORMAT" = "sarif" ] || [ "$SCAN_ALL" = true ]; then
    echo -e "${YELLOW}Generating combined SARIF report...${NC}"

    # Merge all SARIF files
    jq -s '.[0] * {runs: [.[] | .runs[]] | group_by(.tool.driver.name) | map({tool: .[0].tool, results: map(.results[]) | flatten})}' \
        "$OUTPUT_DIR"/*.sarif > "$OUTPUT_DIR/combined-scan.sarif" 2>/dev/null || true
fi

# Exit with error if vulnerabilities found and flag is set
if [ "$EXIT_ON_VULNERABILITY" = true ] && [ "$TOTAL_VULNERABILITIES" -gt 0 ]; then
    echo -e "${RED}Exiting with error due to vulnerabilities${NC}"
    exit 1
fi

exit 0
