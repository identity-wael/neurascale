# Claude Code Instructions for NeuraScale

## Python Version Requirement

**IMPORTANT**: This project uses **Python 3.12.11** exclusively.

- The system Python is located at: `/opt/homebrew/bin/python3.12`
- All virtual environments must use Python 3.12.11
- Do NOT use Python 3.12.5 or any other version

## Virtual Environment Setup

To set up or fix virtual environments, run:

```bash
./scripts/dev-tools/setup-venvs.sh
```

This script will:

- Verify Python 3.12.11 is available
- Create/recreate venvs with the correct Python version
- Install requirements automatically

## Common Virtual Environments

1. **Main Project**: `./venv/`

   - Activate: `source venv/bin/activate`

2. **Neural Engine**: `./neural-engine/venv/`
   - Activate: `source neural-engine/venv/bin/activate`
   - Used by pre-commit hooks for black formatting

## Pre-commit Hooks

The project uses pre-commit hooks that require specific Python versions:

- Black formatter runs in the neural-engine venv
- The script `scripts/dev-tools/run-black.sh` ensures correct Python version

## Linting and Type Checking Commands

When completing tasks, always run:

```bash
# For neural-engine code
cd neural-engine
source venv/bin/activate
black .
flake8 .
mypy .

# For main project
source venv/bin/activate
npm run lint      # For frontend code
npm run typecheck # For frontend type checking
```

## Common Issues and Solutions

### Issue: "Python 3.12.5 has a memory safety issue..."

**Solution**: The venv is using the wrong Python version. Run `./scripts/dev-tools/setup-venvs.sh`

### Issue: Black failing in pre-commit hooks

**Solution**: The neural-engine venv needs to be recreated with Python 3.12.11

### Issue: Module not found errors

**Solution**: Ensure you're in the correct venv and requirements are installed

## Development Workflow

1. Always verify Python version before starting work:

   ```bash
   python --version  # Should show Python 3.12.11
   ```

2. Use the appropriate venv for the code you're working on

3. Run linting/formatting before committing

4. If CI/CD fails with Python version issues, check and fix local venvs first
