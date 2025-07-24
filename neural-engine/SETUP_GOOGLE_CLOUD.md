# Setting Up Google Cloud Credentials

## Quick Steps

1. **Authenticate with Google Cloud:**

```bash
gcloud auth login
```

2. **Run the setup script:**

```bash
cd /Users/weg/NeuraScale/neurascale/neural-engine
./scripts/setup-gcp-auth.sh
```

3. **Copy the service account key:**
   After the script completes, it will create a file called `neural-engine-ci-key.json`.
   Copy its contents:

```bash
cat neural-engine-ci-key.json | pbcopy
```

4. **Add to GitHub Secrets:**

- Go to: https://github.com/identity-wael/neurascale/settings/secrets/actions
- Click "New repository secret"
- Name: `GCP_SA_KEY`
- Value: Paste (Cmd+V) the JSON key contents
- Click "Add secret"

5. **Also add the Project ID secret:**

- Click "New repository secret" again
- Name: `GCP_PROJECT_ID`
- Value: `neurascale`
- Click "Add secret"

6. **Clean up the key file:**

```bash
rm neural-engine-ci-key.json
```

## What the setup script does:

1. Creates a service account: `neural-engine-ci@neurascale.iam.gserviceaccount.com`
2. Grants necessary permissions:
   - Container Registry (for Docker images)
   - Cloud Run (for API deployment)
   - Cloud Functions (for data ingestion)
   - Pub/Sub (for real-time streaming)
   - Secret Manager (for secure storage)
3. Enables required Google Cloud APIs
4. Generates a service account key

## Verify Everything Works

After adding the secrets, the PR checks should:

- ✅ Test Neural Engine (already passing!)
- ✅ Build Docker Images (will work with secrets)
- ✅ Deploy to staging/production (on merge to main)

## Troubleshooting

If you get permission errors, make sure you have these roles in the neurascale project:

- `roles/iam.serviceAccountAdmin`
- `roles/resourcemanager.projectIamAdmin`

You can check your roles with:

```bash
gcloud projects get-iam-policy neurascale \
  --flatten="bindings[].members" \
  --filter="bindings.members:identity@wael.ai" \
  --format="table(bindings.role)"
```
