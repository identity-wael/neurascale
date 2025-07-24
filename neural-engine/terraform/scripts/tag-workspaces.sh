#!/bin/bash

# Add neural-engine tag to workspaces

cat > ~/.terraformrc <<EOF
credentials "app.terraform.io" {
  token = "$TF_CLOUD_TOKEN"
}
EOF

terraform workspace select production
terraform workspace tag add neural-engine

terraform workspace select staging
terraform workspace tag add neural-engine

terraform workspace select development
terraform workspace tag add neural-engine

echo "Added neural-engine tag to all workspaces"
