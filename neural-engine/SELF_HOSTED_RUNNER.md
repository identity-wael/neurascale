# Self-Hosted GitHub Actions Runner Setup

This guide helps you set up a self-hosted runner to accelerate Neural Engine CI/CD builds.

## Benefits

- **Faster builds**: Dependencies are pre-cached, no download time
- **Cost savings**: No GitHub Actions minutes consumed
- **Local testing**: Test changes before pushing
- **Resource control**: Use your machine's full capabilities

## Quick Setup

### 1. Install Runner

```bash
cd neural-engine
./setup-github-runner.sh
```

### 2. Configure Runner

1. Go to: https://github.com/identity-wael/neurascale/settings/actions/runners/new
2. Get your runner token
3. Configure the runner:

```bash
cd ~/actions-runner
./config.sh --url https://github.com/identity-wael/neurascale \
  --token YOUR_RUNNER_TOKEN \
  --name neurascale-local \
  --labels self-hosted,neural-engine,macOS \
  --work _work
```

### 3. Prepare Cache

Set up pre-cached dependencies:

```bash
cd neural-engine
./prepare-runner-cache.sh
```

### 4. Start Runner

#### Option A: Run interactively

```bash
cd ~/actions-runner
./run.sh
```

#### Option B: Install as service (macOS)

```bash
cd ~/actions-runner
./svc.sh install
./svc.sh start
```

Check service status:

```bash
./svc.sh status
```

## How It Works

1. **Workflow Detection**: The CI workflow automatically uses self-hosted runners for neural-engine branches
2. **Cached Dependencies**: Python packages are pre-installed and cached
3. **Fallback**: If self-hosted runner is offline, jobs run on GitHub-hosted runners

## Performance Comparison

| Task                 | GitHub-Hosted | Self-Hosted        |
| -------------------- | ------------- | ------------------ |
| Setup Python         | ~30s          | 0s (pre-installed) |
| Install Dependencies | ~5-10 min     | ~30s (cached)      |
| Total Test Time      | ~12-15 min    | ~2-3 min           |

## Managing the Runner

### Stop runner

```bash
cd ~/actions-runner
./svc.sh stop  # If installed as service
# Or Ctrl+C if running interactively
```

### Update runner

```bash
cd ~/actions-runner
./svc.sh stop
./config.sh remove --token YOUR_REMOVAL_TOKEN
# Then reinstall with setup script
```

### View logs

```bash
cd ~/actions-runner
tail -f _diag/Runner_*.log
```

## Troubleshooting

### Runner appears offline

1. Check if runner is running: `./svc.sh status`
2. Check logs: `tail -f _diag/Runner_*.log`
3. Restart: `./svc.sh stop && ./svc.sh start`

### Permission issues

```bash
# Fix permissions
chmod -R 755 ~/actions-runner
```

### Cache issues

```bash
# Rebuild cache
cd neural-engine
rm -rf ~/.neural-engine-cache
./prepare-runner-cache.sh
```

## Security Notes

- The runner has access to your repository code
- It runs with your user permissions
- Only use on trusted networks
- Keep your runner token secure

## Advanced Configuration

### Resource Limits

Edit `~/actions-runner/.env`:

```bash
# Limit CPU usage
ACTIONS_RUNNER_WORKER_PROCESSES=4

# Set memory limit
ACTIONS_RUNNER_WORKER_MEMORY_MB=8192
```

### Custom Labels

Add labels during configuration:

```bash
--labels self-hosted,neural-engine,macOS,GPU,high-memory
```

Then target specific runners in workflows:

```yaml
runs-on: [self-hosted, GPU]
```
