# Stripe Billing Setup for NeuraScale Console

This guide explains how to set up Stripe billing for the NeuraScale Console application.

## Prerequisites

1. A Stripe account (create one at https://stripe.com)
2. The console app running locally or deployed

## Setup Steps

### 1. Get Stripe API Keys

1. Log into your Stripe dashboard
2. Navigate to Developers → API Keys
3. Copy your:
   - Publishable key (starts with `pk_test_` for test mode)
   - Secret key (starts with `sk_test_` for test mode)

### 2. Create Products and Prices

In your Stripe dashboard:

1. Go to Products → Add Product
2. Create the following products:

#### Starter Plan

- Name: NeuraScale Starter
- Price: $49/month
- Recurring: Monthly

#### Professional Plan

- Name: NeuraScale Professional
- Price: $199/month
- Recurring: Monthly

#### Enterprise Plan

- Name: NeuraScale Enterprise
- Price: Custom (contact sales)
- Recurring: Monthly

3. Copy the price IDs for each plan (starts with `price_`)

### 3. Configure Webhook

1. In Stripe Dashboard, go to Developers → Webhooks
2. Add endpoint:
   - Endpoint URL: `https://your-console-domain.com/api/stripe/webhook`
   - Events to send:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
3. Copy the webhook secret (starts with `whsec_`)

### 4. Set Environment Variables

Add these to your `.env.local` file:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Stripe Price IDs
STRIPE_PRICE_STARTER_MONTHLY=price_starter_monthly_id
STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_professional_monthly_id
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_enterprise_monthly_id

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3001
```

### 5. Run Database Migrations

```bash
cd console
npx prisma migrate dev
```

### 6. Configure Customer Portal

1. Go to Stripe Dashboard → Settings → Billing → Customer Portal
2. Enable the portal
3. Configure which features customers can access:
   - Update payment methods
   - Cancel subscriptions
   - View invoices
   - Update billing address

## Features Implemented

### User Features

- **Pricing Page** (`/pricing`): Display all available plans
- **Billing Dashboard** (`/billing`): View current plan, usage, and invoices
- **Stripe Checkout**: Secure payment flow
- **Customer Portal**: Manage subscription and payment methods

### Technical Implementation

- **Database Models**: Subscription, Invoice, and UsageRecord models
- **API Routes**:
  - `/api/stripe/create-checkout-session`: Create Stripe checkout
  - `/api/stripe/webhook`: Handle Stripe webhooks
  - `/api/stripe/billing-info`: Get user's billing information
  - `/api/stripe/create-portal-session`: Access Stripe customer portal
- **Security**: Firebase auth tokens required for all API calls

## Testing

### Test Cards

Use these test card numbers in Stripe's test mode:

- Success: `4242 4242 4242 4242`
- Requires auth: `4000 0025 0000 3155`
- Declined: `4000 0000 0000 9995`

### Test Webhook Locally

Use Stripe CLI to forward webhooks to your local server:

```bash
stripe listen --forward-to localhost:3001/api/stripe/webhook
```

## Usage Tracking (Optional)

To implement usage-based billing:

1. Track resource usage in the UsageRecord table
2. Create usage records via Stripe API
3. Configure usage-based prices in Stripe

Example:

```typescript
// Track neural processor hours
await prisma.usageRecord.create({
  data: {
    userId: user.id,
    resourceType: "NEURAL_PROCESSOR",
    quantity: hoursUsed,
    unitPrice: 10, // $0.10 per hour
    totalPrice: hoursUsed * 10,
    periodStart: startTime,
    periodEnd: endTime,
  },
});
```

## Going Live

1. Switch to live API keys in production
2. Create live products and prices
3. Update webhook endpoint to production URL
4. Test the complete flow with real cards

## Support

For issues or questions:

- Stripe Documentation: https://stripe.com/docs
- NeuraScale Support: support@neurascale.io
