# Cloud Functions Build Permission Fix

## Issue

Cloud Functions deployment failing with: "Build failed with status: FAILURE. Could not build the function due to a missing permission on the build service account"

## Root Causes

1. Cloud Build service account lacks necessary permissions
2. Missing access to Cloud Functions staging buckets
3. Service account impersonation permissions needed

## Applied Fixes

### 1. Enhanced Cloud Build Permissions

Added the following roles to the Cloud Build service account:

- `roles/artifactregistry.reader` - Read base images
- `roles/cloudbuild.serviceAgent` - Service agent role

### 2. Cloud Build Service Agent Permissions

Added permissions for the service agent account (`service-PROJECT_NUMBER@gcp-sa-cloudbuild.iam.gserviceaccount.com`):

- `roles/cloudbuild.serviceAgent`
- `roles/artifactregistry.reader`
- `roles/storage.objectViewer`
- `roles/iam.serviceAccountUser` on the ingestion service account

### 3. Storage Bucket Access

Granted Cloud Build accounts access to:

- Custom functions bucket: `${project_id}-gcf-source-${environment}`
- Default GCF staging bucket: `gcf-sources-${project_number}-${region}`

## Deployment Steps

1. Apply Terraform changes:

```bash
terraform plan
terraform apply
```

2. Wait for permissions to propagate (1-2 minutes)

3. Retry Cloud Functions deployment

## Additional Troubleshooting

If the issue persists:

1. **Check if the staging bucket exists:**

```bash
gsutil ls gs://gcf-sources-221358080383-northamerica-northeast1/
```

2. **Verify service account permissions:**

```bash
gcloud projects get-iam-policy staging-neurascale --flatten="bindings[].members" --filter="bindings.members:serviceAccount:221358080383@cloudbuild.gserviceaccount.com"
```

3. **Check Cloud Build logs:**

```bash
gcloud builds log b8b5c38f-f33d-481e-9c91-ab24ddc15022 --region=northamerica-northeast1
```

4. **Ensure the neural-ingestion service account exists:**

```bash
gcloud iam service-accounts describe neural-ingestion-stag@staging-neurascale.iam.gserviceaccount.com
```

## Alternative Quick Fix (if urgent)

Grant broader permissions temporarily:

```bash
# Grant Cloud Build Editor role (reduce after deployment)
gcloud projects add-iam-policy-binding staging-neurascale \
  --member="serviceAccount:221358080383@cloudbuild.gserviceaccount.com" \
  --role="roles/editor"

# Grant service agent role
gcloud projects add-iam-policy-binding staging-neurascale \
  --member="serviceAccount:service-221358080383@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.serviceAgent"
```

## Prevention

For future deployments:

1. Always ensure Cloud Build has proper permissions before deploying functions
2. Pre-create staging buckets with correct permissions
3. Use Terraform to manage all Cloud Functions deployments
