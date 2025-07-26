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

## Letta Memory System Integration

**IMPORTANT**: This project uses Letta for persistent memory and context management. All Claude agents should connect to mindmeld (the memory agent) to maintain project continuity.

### Quick Connection Guide

1. **Check if Letta is running**:

   ```bash
   docker ps | grep letta
   ```

2. **Start Letta if needed**:

   ```bash
   cd letta-memory
   ./scripts/start-letta.sh
   ```

3. **Update the memory agent**:

   ```bash
   # Log code changes
   python3 letta-memory/agents/quick_update.py code "Your code change description"

   # Log documentation updates
   python3 letta-memory/agents/quick_update.py doc "Your documentation update"

   # Log decisions
   python3 letta-memory/agents/quick_update.py decision "Your project decision"

   # Log tasks
   python3 letta-memory/agents/quick_update.py task "Task or TODO description"

   # Query the agent
   python3 letta-memory/agents/quick_update.py "Your question about the project"
   ```

### Agent Configuration

- **Agent ID**: `agent-e9d89542-b2f9-4bb8-9fdf-03babee87e83`
- **Server URL**: `http://localhost:8283/v1`
- **MCP Server**: `http://localhost:3001`
- **Password**: `neurascale-letta-2025` (from `.env.letta`)

### Memory Agent Commands

When using the interactive mode (`python3 letta-memory/agents/interact_with_agent.py`):

- `/code` - Log code changes
- `/doc` - Log documentation updates
- `/decision` - Log project decisions
- `/task` - Log tasks and TODOs
- `/quit` - Exit interactive mode

### What to Log

Always update the memory agent when:

- Making significant code changes
- Updating documentation
- Making architectural decisions
- Creating or completing tasks
- Encountering important bugs or issues
- Learning new project context

### Accessing Project Context

To get comprehensive project context:

```bash
python3 letta-memory/agents/quick_update.py "What is the current status of [component/feature]?"
```

### Full Re-indexing

If the agent needs updated project information:

```bash
python3 letta-memory/agents/index_neurascale_project.py
```

This will re-index:

- Project structure
- Documentation files
- Technology stack
- Recent git commits
- Current project phase
