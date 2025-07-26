# Environment Variables - Console App

## Required Variables

### 🗄️ Database

| Variable              | Description                | Example            | Required |
| --------------------- | -------------------------- | ------------------ | -------- |
| `DATABASE_URL`        | Direct database connection | `postgresql://...` | ✅ Yes   |
| `DATABASE_URL_POOLED` | Pooled connection string   | `postgresql://...` | ✅ Yes   |

### 💳 Stripe Billing

| Variable                             | Description                     | Example       | Required |
| ------------------------------------ | ------------------------------- | ------------- | -------- |
| `STRIPE_SECRET_KEY`                  | Stripe secret API key           | `sk_test_...` | ✅ Yes   |
| `STRIPE_WEBHOOK_SECRET`              | Webhook endpoint signing secret | `whsec_...`   | ✅ Yes   |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Public Stripe key               | `pk_test_...` | ✅ Yes   |
| `STRIPE_PRICE_STARTER_MONTHLY`       | Starter plan price ID           | `price_...`   | ✅ Yes   |
| `STRIPE_PRICE_PROFESSIONAL_MONTHLY`  | Professional plan price ID      | `price_...`   | ✅ Yes   |
| `STRIPE_PRICE_ENTERPRISE_MONTHLY`    | Enterprise plan price ID        | `price_...`   | ❌ No    |

### 🔐 Firebase Admin

| Variable                | Description                 | Example                 | Required |
| ----------------------- | --------------------------- | ----------------------- | -------- |
| `FIREBASE_CLIENT_EMAIL` | Service account email       | `firebase-adminsdk@...` | ✅ Yes   |
| `FIREBASE_PRIVATE_KEY`  | Service account private key | `-----BEGIN PRIVATE...` | ✅ Yes   |

## Setup Instructions

1. **Create `.env.local` file**:

   ```bash
   cp .env.example .env.local
   ```

2. **Configure Database** (Neon):

   - Get connection strings from Neon dashboard
   - Use pooled connection for serverless

3. **Configure Stripe**:

   - Get API keys from Stripe dashboard
   - Create products and price IDs
   - Set up webhook endpoint

4. **Configure Firebase**:
   - Download service account JSON
   - Extract client email and private key
   - Format private key (replace `\n` with actual newlines)

## Example `.env.local`

```bash
# Database
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
DATABASE_URL_POOLED="postgresql://user:pass@host-pooler/db?sslmode=require"

# Stripe
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_PRICE_STARTER_MONTHLY="price_..."
STRIPE_PRICE_PROFESSIONAL_MONTHLY="price_..."

# Firebase
FIREBASE_CLIENT_EMAIL="firebase-adminsdk@project.iam.gserviceaccount.com"
FIREBASE_PRIVATE_KEY="<paste-private-key-here>"
```

## Security Notes

- Store Firebase private key securely
- Never expose Stripe secret key to client
- Use webhook secrets to verify Stripe events
- Rotate all keys regularly
- Use test keys for development
