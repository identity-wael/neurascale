---
layout: doc
title: Neon Database
---

# Neon Database Setup & Branch Management

This guide covers Neon database integration, branch management, and workflows for the NeuraScale project.

## Overview

Neon is a serverless Postgres database that provides:

- 🌿 Git-like branching for databases
- ⚡ Instant database provisioning
- 🔄 Automatic scaling
- 💾 Point-in-time recovery
- 🌍 Global distribution

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   GitHub PR     │────▶│  GitHub      │────▶│    Neon     │
│   (Trigger)     │     │  Actions     │     │  Database   │
└─────────────────┘     └──────────────┘     └─────────────┘
                               │                      │
                               ▼                      ▼
                        ┌──────────────┐     ┌─────────────┐
                        │    Vercel    │────▶│  PR Branch  │
                        │   Preview    │     │  Database   │
                        └──────────────┘     └─────────────┘
```

## Branch Strategy

### Production Branch

- **Name**: `main` (default)
- **Purpose**: Production database
- **Access**: Read/write for production app
- **Backups**: Automatic daily backups

### Preview Branches

- **Name**: `preview/pr-{number}-{branch-name}`
- **Purpose**: Isolated testing for PRs
- **Lifecycle**: Created on PR open, deleted on close
- **Access**: Full access for testing

### Development Branch

- **Name**: `dev` (optional)
- **Purpose**: Shared development database
- **Access**: Team development

## Setup Instructions

### 1. Neon Project Setup

1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Note your project ID and connection details

### 2. GitHub Configuration

Add to repository secrets:

- `NEON_API_KEY`: Your Neon API key
- `NEON_PROJECT_ID`: Your project ID (as variable)

### 3. Environment Variables

```bash
# .env.local
DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require

# For pooled connections
DATABASE_URL_POOLED=postgresql://user:pass@host-pooler/neondb?sslmode=require
```

## Workflows

### PR Branch Creation

When a PR is opened, the workflow automatically:

1. Creates a new database branch
2. Names it `preview/pr-{number}-{branch-name}`
3. Provides connection string to Vercel
4. Runs migrations if configured

```yaml
# .github/workflows/neon_workflow.yml
- name: Create Neon Branch
  uses: neondatabase/create-branch-action@v5
  with:
    project_id: ${{ vars.NEON_PROJECT_ID }}
    branch_name: preview/pr-${{ github.event.number }}-${{ needs.setup.outputs.branch }}
    api_key: ${{ secrets.NEON_API_KEY }}
```

### Branch Cleanup

Branches are managed based on PR status:

- **Merged PRs**: Branch retained for debugging
- **Closed PRs**: Branch deleted automatically
- **Old branches**: Weekly cleanup of merged PR branches > 7 days

```yaml
# Only delete if PR closed without merging
if: |
  github.event_name == 'pull_request' &&
  github.event.action == 'closed' &&
  github.event.pull_request.merged == false
```

### Manual Cleanup

Run the cleanup workflow manually:

1. Go to Actions → "Cleanup Old Neon Branches"
2. Click "Run workflow"
3. Set retention days (default: 7)
4. Run

## Database Migrations

### Prisma Setup (Example)

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
}
```

### Running Migrations

```bash
# Generate migration
npx prisma migrate dev --name add_users

# Apply migrations
npx prisma migrate deploy

# Reset database
npx prisma migrate reset
```

### CI/CD Integration

```yaml
# Run migrations on PR branches
- name: Run Migrations
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ steps.create_neon_branch.outputs.db_url }}
```

## Connection Management

### Connection Strings

```typescript
// Direct connection (for migrations)
const directUrl = process.env.DATABASE_URL

// Pooled connection (for app queries)
const pooledUrl = process.env.DATABASE_URL_POOLED

// Prisma configuration
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL_POOLED")
  directUrl = env("DATABASE_URL")
}
```

### Connection Pooling

Use pooled connections for:

- Serverless functions
- High-concurrency apps
- Edge functions

Use direct connections for:

- Migrations
- Database administration
- Long-running queries

## CLI Usage

### Install Neon CLI

```bash
# Install globally
npm install -g neonctl

# Authenticate
neonctl auth
```

### Common Commands

```bash
# List branches
neonctl branches list --project-id <id>

# Create branch
neonctl branches create \
  --project-id <id> \
  --name feature/new-feature

# Get connection string
neonctl cs <branch-id> --project-id <id>

# Delete branch
neonctl branches delete <branch-id> --project-id <id>
```

## Best Practices

### 1. Branch Naming

- Use descriptive names
- Include PR number for tracking
- Follow pattern: `preview/pr-{number}-{feature}`

### 2. Data Management

- Don't use production data in preview branches
- Use seed scripts for test data
- Clean sensitive data before branching

### 3. Performance

- Use connection pooling
- Close connections properly
- Monitor query performance
- Use appropriate indexes

### 4. Security

- Rotate API keys regularly
- Use least-privilege access
- Enable IP allowlisting
- Audit database access

## Troubleshooting

### Common Issues

#### 1. "Connection refused"

- Check connection string
- Verify SSL mode
- Check IP allowlist

#### 2. "Branch already exists"

- Branch wasn't cleaned up
- Manual deletion required
- Check cleanup workflow

#### 3. "Timeout errors"

- Use pooled connections
- Check query optimization
- Verify network connectivity

### Debug Commands

```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"

# Check branch status
neonctl branches get <branch-id> --project-id <id>

# View branch tree
neonctl branches list --project-id <id> --tree
```

## Advanced Topics

### Point-in-Time Recovery

```bash
# Create branch from specific timestamp
neonctl branches create \
  --project-id <id> \
  --name recovery-branch \
  --parent-timestamp "2024-01-15T10:30:00Z"
```

### Database Metrics

Monitor via Neon console:

- Active connections
- Database size
- Compute usage
- Query performance

### Autoscaling Configuration

```typescript
// Configure in Neon console
{
  "autoscaling_limit_min_cu": 0.25,
  "autoscaling_limit_max_cu": 2,
  "suspend_timeout_seconds": 300
}
```

### Integration with ORMs

#### Prisma

```typescript
// prisma/client.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL_POOLED,
    },
  },
});
```

#### Drizzle

```typescript
// db/client.ts
import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);
```

## Resources

- [Neon Documentation](https://neon.tech/docs)
- [Neon CLI Reference](https://neon.tech/docs/reference/cli-reference)
- [Database Branching Guide](https://neon.tech/docs/guides/branching)
- [GitHub Actions Integration](https://neon.tech/docs/guides/branching-github-actions)
