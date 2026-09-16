# Claude Code Instructions for NeuraScale

## Python Version Requirement

**IMPORTANT**: This project uses **Python 3.13** (latest version).

- The system Python is located at: `/opt/homebrew/bin/python3.13`
- All virtual environments must use Python 3.13
- Dockerfiles have been updated to use Python 3.13 base images

## Virtual Environment Setup

To set up or fix virtual environments, run:

```bash
./scripts/dev-tools/setup-venvs.sh
```

This script will:

- Verify Python 3.13 is available
- Create/recreate venvs with the correct Python version
- Install requirements automatically

## Common Virtual Environments

1. **Main Project**: `./venv/`

   - Activate: `source venv/bin/activate`

2. **Neural Engine**: `./neural-engine/venv/`
   - Activate: `source neural-engine/venv/bin/activate`
   - Used by pre-commit hooks for black formatting

## How to Activate the Correct Virtual Environment

Always check which code you're working on to determine the correct venv:

```bash
# For main project code (frontend, general tasks)
cd /Users/weg/NeuraScale/neurascale
source venv/bin/activate

# For neural-engine code (backend, Python development)
cd /Users/weg/NeuraScale/neurascale
source neural-engine/venv/bin/activate

# To verify you're in the correct venv
python --version  # Should show Python 3.13.x
which python      # Should show path within the venv directory
```

**Important**: If you see any version other than Python 3.13, the venv is incorrect. Run `./scripts/dev-tools/setup-venvs.sh` to fix it.

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

## Update Mindmeld Before Committing

**IMPORTANT**: Always update mindmeld with your changes before committing:

```bash
# Quick update for simple changes
cd /Users/weg/NeuraScale/neurascale
python3 letta-memory/agents/fast_mindmeld.py code "Brief description of what you implemented"

# Examples:
python3 letta-memory/agents/fast_mindmeld.py code "Added device interface API endpoints"
python3 letta-memory/agents/fast_mindmeld.py code "Fixed CI/CD test cache to include all directories"
python3 letta-memory/agents/fast_mindmeld.py doc "Updated CLAUDE.md with venv instructions"

# For complex changes requiring detailed context
python3 letta-memory/agents/quick_update.py "Detailed description of implementation, challenges, and decisions"
```

This ensures project continuity and helps future Claude sessions understand the codebase state.

## Common Issues and Solutions

### Issue: Python version mismatch

**Solution**: The venv is using the wrong Python version. Run `./scripts/dev-tools/setup-venvs.sh`

### Issue: Black failing in pre-commit hooks

**Solution**: The neural-engine venv needs to be recreated with Python 3.13

### Issue: Module not found errors

**Solution**: Ensure you're in the correct venv and requirements are installed

## Development Workflow

1. Always verify Python version before starting work:

   ```bash
   python --version  # Should show Python 3.13.x
   ```

2. Use the appropriate venv for the code you're working on

3. Run linting/formatting before committing

4. If CI/CD fails with Python version issues, check and fix local venvs first

## Mindmeld Memory System

**IMPORTANT**: This project uses Letta/mindmeld for persistent memory and context management. All Claude agents should connect to mindmeld to maintain project continuity and access shared knowledge.

### Quick Start Guide

1. **Check if mindmeld is running**:

   ```bash
   docker-compose -f letta-memory/docker-compose.letta.yml ps
   ```

2. **Start mindmeld services if needed**:

   ```bash
   cd /Users/weg/NeuraScale/neurascale
   docker-compose -f letta-memory/docker-compose.letta.yml up -d
   ```

### Three-Tier Speed System

Choose the appropriate interface based on your needs:

#### ⚡ Lightning Tier: <20ms (Pre-computed Responses)

```bash
# FASTEST: Instant responses for common queries
python3 letta-memory/agents/lightning_mindmeld.py "status"
python3 letta-memory/agents/lightning_mindmeld.py "backend"
python3 letta-memory/agents/lightning_mindmeld.py "architecture"
python3 letta-memory/agents/lightning_mindmeld.py "progress"
python3 letta-memory/agents/lightning_mindmeld.py "health"
python3 letta-memory/agents/lightning_mindmeld.py "tech"
```

**Available keywords**: status, backend, architecture, progress, health, tech

#### 🚀 Fast Tier: 1-3s (FastAPI with Caching)

```bash
# FAST: Full responses with intelligent caching
python3 letta-memory/agents/fast_mindmeld.py "Your message"
python3 letta-memory/agents/fast_mindmeld.py "Tell me about the Neural Engine"
```

**Special message types** (auto-formatted):

```bash
python3 letta-memory/agents/fast_mindmeld.py code "Implemented authentication system"
python3 letta-memory/agents/fast_mindmeld.py doc "Updated API documentation"
python3 letta-memory/agents/fast_mindmeld.py decision "Chose FastAPI over Flask"
python3 letta-memory/agents/fast_mindmeld.py task "Need to implement user roles"
```

#### 📡 Reliable Tier: 5-10s (Direct Letta)

```bash
# RELIABLE: Comprehensive responses with full memory access
python3 letta-memory/agents/quick_update.py "Complex question requiring full context"
```

### Service Configuration

- **Agent ID**: `agent-e9d89542-b2f9-4bb8-9fdf-03babee87e83` (mindmeld)
- **Letta Server**: `http://localhost:8283/v1`
- **FastAPI**: `http://localhost:8000`
- **Lightning API**: `http://localhost:8001`
- **MCP Server**: `http://localhost:3001`
- **Password**: `neurascale-letta-2025`

### Working Directory

**CRITICAL**: Always run mindmeld commands from the project root:

```bash
cd /Users/weg/NeuraScale/neurascale
# Then run any mindmeld command
```

### What to Log with Mindmeld

Always update mindmeld when:

- Making significant code changes
- Updating documentation
- Making architectural decisions
- Creating or completing tasks
- Encountering important bugs or issues
- Learning new project context

### Advanced Usage

#### Health Monitoring

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/stats
```

#### Interactive Mode

```bash
# For extended conversations (avoid for simple queries)
python3 letta-memory/agents/interact_with_agent.py
```

#### Batch Updates

```bash
# Update multiple changes efficiently
python3 letta-memory/agents/fast_mindmeld.py "Batch update: [list changes]"
```

#### Speed Testing

```bash
# Compare all tiers
python3 letta-memory/scripts/test-speed.py
```

### Troubleshooting

#### Connection Issues

1. Verify working directory: `pwd` should show `/Users/weg/NeuraScale/neurascale`
2. Check services: `docker-compose -f letta-memory/docker-compose.letta.yml ps`
3. Restart if needed: `docker-compose -f letta-memory/docker-compose.letta.yml restart`

#### Memory Integrity Check

```bash
# Quick verification
python3 letta-memory/agents/lightning_mindmeld.py "status"
```
