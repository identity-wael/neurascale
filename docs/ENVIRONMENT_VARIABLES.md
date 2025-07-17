# Environment Variables Guide

Complete guide to all environment variables used in the NeuraScale project.

## Overview

Environment variables are used to configure the application for different environments (development, staging, production) without hardcoding sensitive information.

## Variable Categories

### 🎨 Sanity CMS (Required)

These variables are required for the application to build and run:

| Variable                         | Description                    | Example      | Required |
| -------------------------------- | ------------------------------ | ------------ | -------- |
| `NEXT_PUBLIC_SANITY_PROJECT_ID`  | Sanity project identifier      | `vvsy01fb`   | ✅ Yes   |
| `NEXT_PUBLIC_SANITY_DATASET`     | Sanity dataset name            | `production` | ✅ Yes   |
| `NEXT_PUBLIC_SANITY_API_VERSION` | Sanity API version             | `2024-01-01` | ✅ Yes   |
| `SANITY_API_TOKEN`               | API token for write operations | `sk...`      | ❌ No    |

### 🗄️ Database (Optional)

For future database integrations:

| Variable              | Description                | Example            | Required |
| --------------------- | -------------------------- | ------------------ | -------- |
| `DATABASE_URL`        | Direct database connection | `postgresql://...` | ❌ No    |
| `DATABASE_URL_POOLED` | Pooled connection string   | `postgresql://...` | ❌ No    |

### 📧 Email Configuration (Optional)

For contact form functionality:

| Variable     | Description                 | Example                  | Required |
| ------------ | --------------------------- | ------------------------ | -------- |
| `EMAIL_USER` | Sender email address        | `contact@neurascale.com` | ❌ No    |
| `EMAIL_PASS` | Email password/app password | `app-specific-password`  | ❌ No    |
| `EMAIL_TO`   | Recipient email address     | `admin@neurascale.com`   | ❌ No    |

### 🌐 Google Services (Optional)

For analytics and maps:

| Variable                          | Description           | Example      | Required |
| --------------------------------- | --------------------- | ------------ | -------- |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Google Maps API key   | `AIza...`    | ❌ No    |
| `NEXT_PUBLIC_GA4_MEASUREMENT_ID`  | Google Analytics 4 ID | `G-XXXXXXXX` | ❌ No    |

### 🚀 Deployment (Platform-specific)

For Vercel deployments:

| Variable     | Description             | Example              | Required |
| ------------ | ----------------------- | -------------------- | -------- |
| `VERCEL_URL` | Auto-injected by Vercel | `project.vercel.app` | Auto     |
| `VERCEL_ENV` | Environment name        | `production`         | Auto     |
| `NODE_ENV`   | Node environment        | `production`         | Auto     |

## Setup Instructions

### Local Development

1. **Create `.env.local` file**:

   ```bash
   cd apps/web
   cp .env.example .env.local
   ```

2. **Edit `.env.local`**:

   ```bash
   # Required
   NEXT_PUBLIC_SANITY_PROJECT_ID=vvsy01fb
   NEXT_PUBLIC_SANITY_DATASET=production
   NEXT_PUBLIC_SANITY_API_VERSION=2024-01-01

   # Optional
   SANITY_API_TOKEN=your-token-here
   EMAIL_USER=your-email@gmail.com
   # EMAIL_PASS - Generate app-specific password from Gmail
   ```

### Vercel Production

1. **Navigate to Vercel Dashboard**
2. **Select your project**
3. **Go to Settings → Environment Variables**
4. **Add variables**:

   ![Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

5. **Set scope** (Production/Preview/Development)

### GitHub Actions

Add to repository secrets:

```yaml
# .github/workflows/deploy.yml
env:
  NEXT_PUBLIC_SANITY_PROJECT_ID: ${{ vars.SANITY_PROJECT_ID }}
  SANITY_API_TOKEN: ${{ secrets.SANITY_API_TOKEN }}
```

## Variable Details

### Sanity Configuration

#### `NEXT_PUBLIC_SANITY_PROJECT_ID`

- **Purpose**: Identifies your Sanity project
- **Format**: Alphanumeric string
- **Where to find**: Sanity management dashboard
- **Public**: Yes (safe to expose)

#### `NEXT_PUBLIC_SANITY_DATASET`

- **Purpose**: Specifies which dataset to use
- **Options**: `production`, `development`, custom
- **Default**: `production`
- **Public**: Yes

#### `SANITY_API_TOKEN`

- **Purpose**: Authentication for write operations
- **Security**: Keep secret, never commit
- **Permissions**: Editor or Admin
- **Generation**: https://sanity.io/manage

### Email Configuration

#### Setting up Gmail

1. Enable 2-factor authentication
2. Generate app password:
   - Go to https://myaccount.google.com/apppasswords
   - Create new app password
   - Use this instead of regular password

#### Alternative Email Providers

- **SendGrid**: Use API key as `EMAIL_PASS`
- **Mailgun**: Use API key format
- **AWS SES**: Use SMTP credentials

### Google Services

#### Google Maps API

1. Create project in Google Cloud Console
2. Enable Maps JavaScript API
3. Create API key
4. Restrict key to your domains:
   ```
   localhost:3000
   *.vercel.app
   neurascale.com
   ```

#### Google Analytics 4

1. Create property in GA4
2. Get Measurement ID (G-XXXXXXXX)
3. Add to environment variables
4. No additional configuration needed

## Security Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.local
.env.production
```

### 2. Use Different Values Per Environment

```bash
# Development
NEXT_PUBLIC_API_URL=http://localhost:3000

# Production
NEXT_PUBLIC_API_URL=https://api.neurascale.com
```

### 3. Rotate Tokens Regularly

- Set expiration dates
- Rotate every 90 days
- Audit access logs

### 4. Principle of Least Privilege

- Use read-only tokens where possible
- Limit token scope
- Environment-specific access

## Validation

### Required Variables Check

```typescript
// lib/env.ts
const requiredEnvVars = [
  "NEXT_PUBLIC_SANITY_PROJECT_ID",
  "NEXT_PUBLIC_SANITY_DATASET",
  "NEXT_PUBLIC_SANITY_API_VERSION",
];

requiredEnvVars.forEach((envVar) => {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
});
```

### Type-safe Environment Variables

```typescript
// env.d.ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_SANITY_PROJECT_ID: string;
      NEXT_PUBLIC_SANITY_DATASET: string;
      NEXT_PUBLIC_SANITY_API_VERSION: string;
      SANITY_API_TOKEN?: string;
      DATABASE_URL?: string;
      EMAIL_USER?: string;
      EMAIL_PASS?: string;
    }
  }
}
```

## Troubleshooting

### Common Issues

#### "Environment variable not found"

- Check spelling and capitalization
- Ensure `.env.local` exists
- Restart development server
- Clear `.next` cache

#### "Invalid API key"

- Verify key is active
- Check domain restrictions
- Ensure proper formatting
- No extra spaces

#### Variables not updating

```bash
# Clear cache and rebuild
rm -rf .next
npm run dev
```

### Debug Commands

```bash
# List all environment variables
env | grep NEXT_PUBLIC

# Check specific variable
echo $NEXT_PUBLIC_SANITY_PROJECT_ID

# Verify in Node.js
node -e "console.log(process.env.NEXT_PUBLIC_SANITY_PROJECT_ID)"
```

## Platform-Specific Notes

### Vercel

- Automatically injects `VERCEL_*` variables
- Supports environment-specific values
- Preview deployments get unique URLs

### Netlify

- Use `NETLIFY_*` prefix for platform variables
- Supports branch-based deploys
- Environment context available

### Docker

```dockerfile
# Dockerfile
ARG NEXT_PUBLIC_SANITY_PROJECT_ID
ENV NEXT_PUBLIC_SANITY_PROJECT_ID=$NEXT_PUBLIC_SANITY_PROJECT_ID
```

### Railway/Render

- Similar to Vercel
- GUI for variable management
- Automatic HTTPS

## Resources

- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Sanity Environment Setup](https://www.sanity.io/docs/environment-variables)
- [12-Factor App Config](https://12factor.net/config)
