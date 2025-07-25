# Self-Hosted Runner Reliability Recommendations

## Immediate Actions Before Retry

1. **Prevent Computer Sleep/Lock During Workflows**:

   ```bash
   # macOS: Prevent sleep while workflow is running
   caffeinate -d -i -m -s
   ```

2. **Keep Runner Active**:
   - Go to System Preferences → Energy Saver
   - Set "Turn display off after" to Never (temporarily)
   - Uncheck "Put hard disks to sleep when possible"

## Long-term Solutions

### Option 1: Run GitHub Runner as a Service

```bash
# Install the runner as a service to survive lock/sleep
cd ~/actions-runner
sudo ./svc.sh install
sudo ./svc.sh start
```

### Option 2: Use GitHub-Hosted Runners for Critical Jobs

Update `.github/workflows/neural-engine-cicd.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest # Instead of self-hosted
    # ... rest of config
```

### Option 3: Dedicated Runner Machine

- Use a dedicated Mac Mini or old laptop as a runner
- Configure it to never sleep
- Place it on your network for CI/CD only

### Option 4: Hybrid Approach

Use self-hosted for builds (faster) but GitHub-hosted for tests:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest # Reliable for tests

  build:
    runs-on: self-hosted # Fast local builds
```

## Runner Configuration Best Practices

1. **Auto-start on boot**:

   ```bash
   # Create LaunchAgent for auto-start
   sudo ./svc.sh install
   ```

2. **Monitor runner health**:

   ```bash
   # Check runner status
   ./svc.sh status
   ```

3. **Set up runner timeout**:
   Add to workflow:
   ```yaml
   jobs:
     test:
       timeout-minutes: 30 # Fail fast if hung
   ```

## For Your Current Retry

1. Run this command before retrying:

   ```bash
   caffeinate -d -i -m -s &
   ```

   This will prevent your Mac from sleeping.

2. Monitor the workflow actively to ensure it completes.

3. Consider running the runner service installation after this workflow completes successfully.
