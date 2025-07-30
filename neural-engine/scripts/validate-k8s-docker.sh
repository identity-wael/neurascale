#!/bin/bash

# Script to validate alignment between Docker images and Kubernetes deployments

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKER_DIR="${BASE_DIR}/neural-engine/docker"
K8S_DIR="${BASE_DIR}/neural-engine/kubernetes"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Validating Docker-Kubernetes Alignment"
echo "========================================"

# Function to extract image from values.yaml
extract_images_from_values() {
    local values_file="${K8S_DIR}/helm/neural-engine/values.yaml"

    echo -e "\n📋 Images defined in Helm values:"

    # Extract main processor image
    local processor_image=$(yq eval '.image.repository + ":" + .image.tag' "$values_file")
    echo "  - Neural Processor: $processor_image"

    # Extract service-specific images
    local device_manager_image=$(yq eval '.deviceManager.image.repository + ":" + .deviceManager.image.tag' "$values_file")
    echo "  - Device Manager: $device_manager_image"

    local api_gateway_image=$(yq eval '.apiGateway.image.repository + ":" + .apiGateway.image.tag' "$values_file")
    echo "  - API Gateway: $api_gateway_image"

    local ml_pipeline_image=$(yq eval '.mlPipeline.image.repository + ":" + .mlPipeline.image.tag' "$values_file")
    echo "  - ML Pipeline: $ml_pipeline_image"

    local mcp_server_image=$(yq eval '.mcpServer.image.repository + ":" + .mcpServer.image.tag' "$values_file")
    echo "  - MCP Server: $mcp_server_image"
}

# Function to check Dockerfile existence
check_dockerfiles() {
    echo -e "\n📦 Checking Dockerfiles:"

    local services=("neural-processor" "device-manager" "api-gateway" "ml-pipeline" "mcp-server")
    local all_exist=true

    for service in "${services[@]}"; do
        local dockerfile="${DOCKER_DIR}/dockerfiles/services/${service}/Dockerfile"
        if [[ -f "$dockerfile" ]]; then
            echo -e "  ${GREEN}✓${NC} $service: Found"
        else
            echo -e "  ${RED}✗${NC} $service: Missing"
            all_exist=false
        fi
    done

    if [[ "$all_exist" == "false" ]]; then
        echo -e "\n${RED}Error: Some Dockerfiles are missing${NC}"
        exit 1
    fi
}

# Function to check deployment templates
check_deployment_templates() {
    echo -e "\n🚀 Checking Kubernetes deployment templates:"

    local deployments=(
        "deployment.yaml:processor"
        "deployment-device-manager.yaml:device-manager"
        "deployment-api-gateway.yaml:api-gateway"
        "deployment-ml-pipeline.yaml:ml-pipeline"
        "deployment-mcp-server.yaml:mcp-server"
    )

    local all_exist=true

    for deployment in "${deployments[@]}"; do
        IFS=':' read -r filename component <<< "$deployment"
        local template="${K8S_DIR}/helm/neural-engine/templates/${filename}"

        if [[ -f "$template" ]]; then
            # Check if the template references the correct image
            if grep -q "${component}" "$template"; then
                echo -e "  ${GREEN}✓${NC} $component: Template exists and configured"
            else
                echo -e "  ${YELLOW}⚠${NC} $component: Template exists but may need configuration"
            fi
        else
            echo -e "  ${RED}✗${NC} $component: Template missing"
            all_exist=false
        fi
    done

    if [[ "$all_exist" == "false" ]]; then
        echo -e "\n${RED}Error: Some deployment templates are missing${NC}"
        exit 1
    fi
}

# Function to validate CI/CD workflow
check_ci_cd() {
    echo -e "\n🔧 Checking CI/CD configuration:"

    local workflow="${BASE_DIR}/.github/workflows/docker-build.yml"

    if [[ -f "$workflow" ]]; then
        echo -e "  ${GREEN}✓${NC} Docker build workflow exists"

        # Check if all services are in the build matrix
        local services=("neural-processor" "device-manager" "api-gateway" "ml-pipeline" "mcp-server")
        local all_in_matrix=true

        for service in "${services[@]}"; do
            if grep -q "$service" "$workflow"; then
                echo -e "  ${GREEN}✓${NC} $service: In build matrix"
            else
                echo -e "  ${RED}✗${NC} $service: Missing from build matrix"
                all_in_matrix=false
            fi
        done

        if [[ "$all_in_matrix" == "false" ]]; then
            echo -e "\n${YELLOW}Warning: Some services are missing from CI/CD workflow${NC}"
        fi
    else
        echo -e "  ${RED}✗${NC} Docker build workflow missing"
    fi
}

# Function to check docker-compose alignment
check_docker_compose() {
    echo -e "\n🐳 Checking Docker Compose configuration:"

    local compose_files=(
        "${DOCKER_DIR}/compose/docker-compose.yml"
        "${DOCKER_DIR}/compose/docker-compose.k8s.yml"
    )

    for compose_file in "${compose_files[@]}"; do
        if [[ -f "$compose_file" ]]; then
            echo -e "  ${GREEN}✓${NC} $(basename "$compose_file"): Found"
        else
            echo -e "  ${YELLOW}⚠${NC} $(basename "$compose_file"): Missing"
        fi
    done
}

# Function to generate alignment report
generate_report() {
    echo -e "\n📊 Alignment Report"
    echo "=================="

    cat << EOF

## Image Repository Pattern
- Repository: gcr.io/development-neurascale/{service-name}
- Tag: latest (or specific version)

## Service Mapping
| Service | Docker Path | K8s Deployment | Status |
|---------|-------------|----------------|--------|
| Neural Processor | services/neural-processor | deployment.yaml | ✓ |
| Device Manager | services/device-manager | deployment-device-manager.yaml | ✓ |
| API Gateway | services/api-gateway | deployment-api-gateway.yaml | ✓ |
| ML Pipeline | services/ml-pipeline | deployment-ml-pipeline.yaml | ✓ |
| MCP Server | services/mcp-server | deployment-mcp-server.yaml | ✓ |

## Next Steps
1. Build images: make docker-build
2. Push to registry: make docker-push
3. Deploy to K8s: make k8s-deploy

EOF
}

# Main execution
main() {
    # Check for required tools
    command -v yq >/dev/null 2>&1 || { echo "yq is required but not installed. Aborting." >&2; exit 1; }

    extract_images_from_values
    check_dockerfiles
    check_deployment_templates
    check_ci_cd
    check_docker_compose
    generate_report

    echo -e "\n${GREEN}✅ Validation complete!${NC}"
}

main "$@"
