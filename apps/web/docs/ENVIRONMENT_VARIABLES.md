# Environment Variables - Marketing Web App

## Required Variables

### 🎨 Sanity CMS

| Variable                         | Description                    | Example      | Required |
| -------------------------------- | ------------------------------ | ------------ | -------- |
| `NEXT_PUBLIC_SANITY_PROJECT_ID`  | Sanity project identifier      | `vvsy01fb`   | ✅ Yes   |
| `NEXT_PUBLIC_SANITY_DATASET`     | Sanity dataset name            | `production` | ✅ Yes   |
| `NEXT_PUBLIC_SANITY_API_VERSION` | Sanity API version             | `2024-01-01` | ✅ Yes   |
| `SANITY_API_TOKEN`               | API token for write operations | `sk...`      | ❌ No    |

## Optional Variables

### 📧 Email Configuration

For contact form functionality:

| Variable     | Description                 | Example                  | Required |
| ------------ | --------------------------- | ------------------------ | -------- |
| `EMAIL_USER` | Sender email address        | `contact@neurascale.com` | ❌ No    |
| `EMAIL_PASS` | Email password/app password | `app-specific-password`  | ❌ No    |
| `EMAIL_TO`   | Recipient email address     | `admin@neurascale.com`   | ❌ No    |

### 🌐 Google Services

For analytics and ads:

| Variable                          | Description           | Example      | Required |
| --------------------------------- | --------------------- | ------------ | -------- |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Google Maps API key   | `AIza...`    | ❌ No    |
| `NEXT_PUBLIC_GA4_MEASUREMENT_ID`  | Google Analytics 4 ID | `G-XXXXXXXX` | ❌ No    |

## Setup Instructions

1. **Create `.env.local` file**:

   ```bash
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
   EMAIL_PASS=# Generate app-specific password from Gmail
   ```

## Type-safe Environment Variables

```typescript
// types/env.d.ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_SANITY_PROJECT_ID: string;
      NEXT_PUBLIC_SANITY_DATASET: string;
      NEXT_PUBLIC_SANITY_API_VERSION: string;
      SANITY_API_TOKEN?: string;
      EMAIL_USER?: string;
      EMAIL_PASS?: string;
      NEXT_PUBLIC_GOOGLE_MAPS_API_KEY?: string;
      NEXT_PUBLIC_GA4_MEASUREMENT_ID?: string;
    }
  }
}
```

## Vercel Deployment

1. Navigate to Vercel Dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add the required variables
5. Set appropriate scope (Production/Preview/Development)

## Security Notes

- Never commit `.env.local` or any file containing secrets
- Use different values for development and production
- Rotate API tokens regularly
- For Gmail, use app-specific passwords, not your main password
