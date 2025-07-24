#!/bin/bash

echo "Terraform Cloud Authentication Setup"
echo "==================================="
echo ""
echo "To authenticate with Terraform Cloud, you need an API token."
echo ""
echo "1. Go to: https://app.terraform.io/app/settings/tokens"
echo "2. Click 'Create an API token'"
echo "3. Name it: 'NeuraScale CLI'"
echo "4. Copy the token"
echo ""
read -p "Paste your Terraform Cloud API token here: " TF_TOKEN

if [ -z "$TF_TOKEN" ]; then
    echo "Error: No token provided"
    exit 1
fi

# Create credentials file
mkdir -p ~/.terraform.d
cat > ~/.terraform.d/credentials.tfrc.json <<EOF
{
  "credentials": {
    "app.terraform.io": {
      "token": "$TF_TOKEN"
    }
  }
}
EOF

chmod 600 ~/.terraform.d/credentials.tfrc.json

echo ""
echo "✓ Token saved to ~/.terraform.d/credentials.tfrc.json"
echo ""
echo "You can now run: terraform init"
