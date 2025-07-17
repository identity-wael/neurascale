# Stripe Billing Integration

This document provides a comprehensive guide for setting up and managing the Stripe billing integration in the NeuraScale console application.

## Overview

The Stripe billing integration provides:

- Subscription management with multiple pricing tiers
- Secure payment processing with Stripe Checkout
- Automated invoice generation
- Customer portal for self-service management
- Usage tracking and billing analytics

## Prerequisites

1. A Stripe account (sign up at https://stripe.com)
2. Firebase authentication configured
3. PostgreSQL database with Prisma

## Setup Instructions

### 1. Stripe Account Configuration

1. **Create a Stripe Account**

   - Sign up at https://stripe.com
   - Complete the account setup process

2. **Get API Keys**

   - Navigate to Developers > API keys
   - Copy your test mode keys:
     - Publishable key (starts with `pk_test_`)
     - Secret key (starts with `sk_test_`)

3. **Create Products and Prices**

   - Go to Products in the Stripe Dashboard
   - Create the following products with monthly pricing:

   ```
   Starter Plan
   - Price: $49/month
   - Product ID: Save this for STRIPE_PRICE_STARTER_MONTHLY

   Professional Plan
   - Price: $199/month
   - Product ID: Save this for STRIPE_PRICE_PROFESSIONAL_MONTHLY

   Enterprise Plan
   - Custom pricing (contact sales)
   - Product ID: Save this for STRIPE_PRICE_ENTERPRISE_MONTHLY
   ```

4. **Configure Webhook Endpoint**
   - Go to Developers > Webhooks
   - Add endpoint: `https://console.neurascale.io/api/stripe/webhook`
   - Select events:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
   - Copy the webhook signing secret

### 2. Environment Variables

Add the following to your `.env.local` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Stripe Price IDs
STRIPE_PRICE_STARTER_MONTHLY=price_starter_monthly_id
STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_professional_monthly_id
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_enterprise_monthly_id

# App Configuration
NEXT_PUBLIC_APP_URL=https://console.neurascale.io
```

### 3. Database Setup

The Prisma schema includes the following billing-related models:

```prisma
model Subscription {
  id                   String    @id @default(cuid())
  stripeCustomerId     String    @unique
  stripeSubscriptionId String?   @unique
  stripePriceId        String?
  status               SubscriptionStatus @default(INCOMPLETE)
  plan                 SubscriptionPlan   @default(FREE)
  currentPeriodStart   DateTime?
  currentPeriodEnd     DateTime?
  cancelAtPeriodEnd    Boolean   @default(false)
  createdAt            DateTime  @default(now())
  updatedAt            DateTime  @updatedAt
  userId               String    @unique
  user                 User      @relation(fields: [userId], references: [id])
}

model Invoice {
  id                String    @id @default(cuid())
  stripeInvoiceId   String    @unique
  amountPaid        Int
  amountDue         Int
  currency          String    @default("usd")
  status            String
  hostedInvoiceUrl  String?
  invoicePdf        String?
  periodStart       DateTime
  periodEnd         DateTime
  createdAt         DateTime  @default(now())
  userId            String
  user              User      @relation(fields: [userId], references: [id])
}

model UsageRecord {
  id                String    @id @default(cuid())
  resourceType      ResourceType
  quantity          Int
  unitPrice         Int
  totalPrice        Int
  periodStart       DateTime
  periodEnd         DateTime
  createdAt         DateTime  @default(now())
  userId            String
  user              User      @relation(fields: [userId], references: [id])
}
```

Run migrations:

```bash
npx prisma migrate dev
```

### 4. Customer Portal Configuration

1. **Enable Customer Portal in Stripe**

   - Go to Settings > Billing > Customer portal
   - Configure the portal settings:
     - Enable subscription cancellation
     - Enable plan switching
     - Enable invoice history
     - Set allowed products for upgrades/downgrades

2. **Configure Return URL**
   - Set return URL to: `https://console.neurascale.io/billing`

## Features

### Pricing Page (`/pricing`)

Displays available subscription tiers with features:

- Free: Basic features for trying out NeuraScale
- Starter ($49/month): For small projects
- Professional ($199/month): For production workloads
- Enterprise: Custom pricing for large organizations

### Billing Dashboard (`/billing`)

Users can:

- View current subscription status
- See usage metrics
- Access invoice history
- Manage subscription (upgrade/downgrade/cancel)
- Access Stripe Customer Portal

### API Endpoints

1. **Create Checkout Session**

   - Endpoint: `POST /api/stripe/create-checkout-session`
   - Creates a Stripe Checkout session for subscription

2. **Webhook Handler**

   - Endpoint: `POST /api/stripe/webhook`
   - Processes Stripe webhook events

3. **Billing Info**

   - Endpoint: `GET /api/stripe/billing-info`
   - Retrieves user's billing information

4. **Create Portal Session**

   - Endpoint: `POST /api/stripe/create-portal-session`
   - Creates a Customer Portal session

5. **Cancel Subscription**
   - Endpoint: `POST /api/stripe/cancel-subscription`
   - Cancels subscription at period end

## Testing

### Test Card Numbers

Use these test card numbers in Stripe's test mode:

- Success: `4242 4242 4242 4242`
- Requires authentication: `4000 0025 0000 3155`
- Declined: `4000 0000 0000 9995`

### Testing Webhooks Locally

Use Stripe CLI for local webhook testing:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local endpoint
stripe listen --forward-to localhost:3001/api/stripe/webhook
```

## Production Deployment

1. **Switch to Live Mode**

   - Update all environment variables with live mode keys
   - Update webhook endpoint to production URL

2. **Security Considerations**

   - Ensure all API routes verify authentication
   - Validate webhook signatures
   - Use HTTPS for all endpoints
   - Store sensitive data securely

3. **Monitoring**
   - Set up alerts for failed payments
   - Monitor webhook failures
   - Track subscription metrics

## Troubleshooting

### Common Issues

1. **Webhook Signature Verification Failed**

   - Ensure `STRIPE_WEBHOOK_SECRET` is correctly set
   - Check that raw request body is used for verification

2. **Firebase Admin Initialization Errors**

   - Verify Firebase Admin environment variables
   - Ensure service account credentials are valid

3. **Database Connection Issues**
   - Check `DATABASE_URL` is correctly set
   - Run `npx prisma generate` after schema changes

### Support

For Stripe-specific issues:

- Documentation: https://stripe.com/docs
- Support: https://support.stripe.com

For NeuraScale integration issues:

- Create an issue in the GitHub repository
- Contact the development team

## Best Practices

1. **Testing**

   - Always test in Stripe test mode first
   - Test all subscription lifecycle events
   - Verify webhook handling

2. **Security**

   - Never expose secret keys in client code
   - Always verify webhook signatures
   - Use environment variables for sensitive data

3. **User Experience**

   - Provide clear pricing information
   - Handle errors gracefully
   - Send confirmation emails for billing events

4. **Compliance**
   - Follow PCI compliance guidelines
   - Implement proper data retention policies
   - Provide clear terms of service
