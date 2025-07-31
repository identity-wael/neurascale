# Branch Protection Requirements

## Production-Level PR Testing Policy

To ensure all PRs undergo full production-identical testing, we require:

### 1. **No Fork PRs**

- All PRs must be created from branches in the main repository
- Fork PRs cannot access secrets needed for full testing
- This ensures every PR can authenticate, build, push, scan, and deploy

### 2. **Required Status Checks**

Before merging any PR, these checks must pass:

- ✅ Docker Build and Push (all services)
- ✅ Trivy Security Scan
- ✅ Google Cloud Authentication
- ✅ Staging Deployment
- ✅ Integration Tests

### 3. **How to Create PRs**

```bash
# 1. Clone the main repository (not a fork)
git clone https://github.com/identity-wael/neurascale.git

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git add .
git commit -m "feat: your feature description"

# 4. Push to the main repository
git push origin feature/your-feature-name

# 5. Create PR from GitHub UI
```

### 4. **External Contributors**

If you're an external contributor:

1. Request repository access from maintainers
2. Or have a maintainer create a branch for your changes
3. This ensures full testing while maintaining security

### 5. **Why This Policy**

- **Production Parity**: PRs test the exact same pipeline as production
- **Early Detection**: Catch all issues before merge, not in production
- **Security**: Maintain secure access to GCP resources
- **Reliability**: Every change is fully validated

This policy ensures we "shift left" - catching all issues during PR review rather than in production deployments.
