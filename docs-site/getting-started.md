---
layout: default
title: Getting Started
permalink: /getting-started/
---

# Getting Started with NeuraScale

This guide will help you get up and running with NeuraScale in minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18.x or higher ([Download](https://nodejs.org/))
- **pnpm** 9.x or higher ([Installation guide](https://pnpm.io/installation))
- **Git** ([Download](https://git-scm.com/))
- A code editor (we recommend [VS Code](https://code.visualstudio.com/))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/identity-wael/neurascale.git
cd neurascale
```

### 2. Install Dependencies

We use pnpm for fast, efficient package management:

```bash
pnpm install
```

This will install all dependencies for the monorepo.

### 3. Configure Environment Variables

Navigate to the web application:

```bash
cd apps/web
```

Copy the example environment file:

```bash
cp .env.example .env.local
```

### 4. Set Up Your Environment

Edit `.env.local` with your configuration:

```env
# Sanity CMS (Required)
NEXT_PUBLIC_SANITY_PROJECT_ID=your_project_id
NEXT_PUBLIC_SANITY_DATASET=production
NEXT_PUBLIC_SANITY_API_VERSION=2024-01-01

# Database (Required for full functionality)
DATABASE_URL=your_neon_database_url

# Google Services (Optional)
NEXT_PUBLIC_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_api_key

# Email (Optional)
EMAIL_USER=your-email@gmail.com
# See docs for app-specific password setup
```

### 5. Start the Development Server

```bash
pnpm dev
```

Your application will be available at:

- Web App: [http://localhost:3000](http://localhost:3000)
- Sanity Studio: [http://localhost:3000/studio](http://localhost:3000/studio)

## Project Structure

```
neurascale/
├── apps/
│   ├── web/              # Main web application
│   └── packages/         # Shared packages
├── console/              # NeuraScale Console
├── docs/                 # Documentation
├── docs-site/           # GitHub Pages site
└── .github/             # GitHub workflows
```

## Next Steps

Now that you have NeuraScale running locally, explore these resources:

1. **[Architecture Overview](/architecture/)** - Understand the platform architecture
2. **[Developer Guide](/developer-guide/)** - Deep dive into development
3. **[API Documentation](/api/)** - Explore available APIs
4. **[Deployment Guide](/deployment/)** - Deploy to production

## Quick Commands

Here are the most common commands you'll use:

```bash
# Development
pnpm dev              # Start dev server
pnpm build            # Build for production
pnpm start            # Start production server

# Code Quality
pnpm lint             # Run ESLint
pnpm format           # Format with Prettier
pnpm typecheck        # Check TypeScript

# Database
pnpm db:push          # Push schema changes
pnpm db:studio        # Open Prisma Studio
```

## Troubleshooting

### Common Issues

**Port 3000 is already in use**

```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 pnpm dev
```

**Module not found errors**

```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Environment variables not loading**

- Ensure `.env.local` exists in `apps/web/`
- Restart the development server
- Check variable names are exact (case-sensitive)

## Getting Help

- 📚 [Documentation](https://docs.neurascale.io)
- 💬 [GitHub Discussions](https://github.com/identity-wael/neurascale/discussions)
- 🐛 [Report Issues](https://github.com/identity-wael/neurascale/issues)
- 📧 [Email Support](mailto:support@neurascale.io)

---

Ready to build something amazing? Let's bridge mind and world together! 🧠🌍
