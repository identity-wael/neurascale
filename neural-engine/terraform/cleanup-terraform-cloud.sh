#!/bin/bash

# Script to remove Terraform Cloud workspaces and revoke access
# This requires a Terraform Cloud API token

set -e

echo "This script will remove Terraform Cloud workspaces and access."
echo "You'll need to provide your Terraform Cloud API token."
echo ""
read -p "Enter your Terraform Cloud API token: " TF_TOKEN

if [ -z "$TF_TOKEN" ]; then
    echo "Error: Token is required"
    exit 1
fi

ORGANIZATION="neurascale"
API_URL="https://app.terraform.io/api/v2"

echo ""
echo "Listing workspaces in organization: $ORGANIZATION"

# List workspaces
WORKSPACES=$(curl -s \
  --header "Authorization: Bearer $TF_TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  "$API_URL/organizations/$ORGANIZATION/workspaces" | \
  jq -r '.data[].id')

if [ -z "$WORKSPACES" ]; then
    echo "No workspaces found or unable to access the organization."
    exit 0
fi

echo "Found workspaces:"
echo "$WORKSPACES"
echo ""

# Delete each workspace
for WORKSPACE_ID in $WORKSPACES; do
    echo "Deleting workspace: $WORKSPACE_ID"
    curl -s -X DELETE \
      --header "Authorization: Bearer $TF_TOKEN" \
      --header "Content-Type: application/vnd.api+json" \
      "$API_URL/workspaces/$WORKSPACE_ID"
    echo "Deleted workspace: $WORKSPACE_ID"
done

echo ""
echo "All workspaces have been deleted."
echo ""
echo "To revoke Terraform Cloud's access to Google Cloud:"
echo "1. Go to https://console.cloud.google.com/iam-admin/iam"
echo "2. Search for any service accounts or workload identity pools related to Terraform Cloud"
echo "3. Remove their IAM permissions"
echo ""
echo "To completely disconnect from Terraform Cloud:"
echo "1. Remove the TF_CLOUD_TOKEN secret from your GitHub repository"
echo "2. Delete the Terraform Cloud organization if no longer needed"
