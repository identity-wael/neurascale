---
layout: doc
title: Google Ads Setup
---

# Google Ads Setup Guide for NeuraScale

## Overview

This guide walks you through setting up Google Ads for NeuraScale, including account creation, API access, and integration with your application.

## Step 1: Create Google Ads Account

1. **Go to Google Ads**: https://ads.google.com
2. **Click "Start Now"**
3. **Create your first campaign** (you can pause it immediately):
   - Campaign Goal: Website traffic
   - Campaign Type: Search
   - Website: https://neurascale.io
   - Business Name: NeuraScale
   - Budget: Set minimum ($1/day, pause after creation)

## Step 2: Get Google Ads Customer ID

1. Once logged in, find your **Customer ID** in the top right corner (format: XXX-XXX-XXXX)
2. Save this ID - you'll need it for API access

## Step 3: Apply for API Access

1. **Go to API Center**: https://ads.google.com/aw/apicenter
2. **Apply for Basic Access**:
   - Use Case: "Website integration for campaign management"
   - Expected API Usage: "Low volume - managing campaigns for neurascale.io"
   - Contact Email: hello@neurascale.io

## Step 4: Create Google Cloud Project

1. **Go to**: https://console.cloud.google.com
2. **Create New Project**: "neurascale-ads"
3. **Enable APIs**:
   ```
   - Google Ads API
   ```

## Step 5: Create OAuth2 Credentials

1. In Google Cloud Console, go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Configure consent screen:
   - App Name: NeuraScale Ads Manager
   - User Support Email: support@neurascale.io
   - Authorized Domains: neurascale.io
4. Create OAuth2 Client:
   - Application Type: **Web application**
   - Name: NeuraScale Ads Web Client
   - Authorized redirect URIs:
     ```
     https://neurascale.io/api/auth/google/callback
     http://localhost:3000/api/auth/google/callback
     ```
5. Download the credentials JSON

## Step 6: Get Refresh Token

1. Use the OAuth2 Playground: https://developers.google.com/oauthplayground
2. Configure settings (gear icon):
   - Use your own OAuth credentials
   - Enter Client ID and Secret from Step 5
3. Select scope: `https://www.googleapis.com/auth/adwords`
4. Authorize and get refresh token

## Step 7: Required Environment Variables

Add these to Vercel:

```bash
# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id

# Optional - for manager accounts
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_customer_id
```

## Step 8: Integration Points

### For Conversion Tracking

Add this to your landing pages:

```html
<!-- Google Ads Conversion Tracking -->
<script
  async
  src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"
></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag("js", new Date());
  gtag("config", "AW-XXXXXXXXX");
</script>
```

### For Remarketing

Add to layout.tsx:

```typescript
<!-- Google Ads Remarketing Tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXX');
  gtag('event', 'page_view', {
    'send_to': 'AW-XXXXXXXXX',
    'value': 'replace with value',
    'items': [{
      'id': 'replace with product id',
      'location_id': 'replace with location',
      'category': 'replace with category',
      'google_business_vertical': 'custom'
    }]
  });
</script>
```

## Step 9: Recommended Campaign Structure

### 1. Brand Campaign

- **Campaign Name**: NeuraScale - Brand
- **Keywords**:
  - neurascale
  - neurascale io
  - neurascale platform
  - neurascale neural prosthetics

### 2. Neural Prosthetics Campaign

- **Campaign Name**: Neural Prosthetics - Search
- **Keywords**:
  - neural prosthetics platform
  - brain computer interface cloud
  - neural data processing
  - BCI infrastructure
  - neural interface development

### 3. Developer Campaign

- **Campaign Name**: Developers - Search
- **Keywords**:
  - neural api platform
  - brain data sdk
  - prosthetics development platform
  - neural computing infrastructure

### 4. Healthcare Campaign

- **Campaign Name**: Healthcare - Search
- **Keywords**:
  - medical neural interface
  - prosthetic control system
  - brain signal processing healthcare
  - clinical BCI platform

## Step 10: Ad Copy Templates

### Responsive Search Ads

**Headlines** (15 max, 30 chars each):

1. Neural Prosthetics Cloud
2. Brain-Computer Interface
3. NeuraScale Platform
4. Process Petabytes of Data
5. Neural Interface SDK
6. Open Source BCI Platform
7. Restore Mobility Today
8. Neural Data Infrastructure
9. Developer-First Platform
10. Clinical Grade BCI

**Descriptions** (4 max, 90 chars each):

1. Open-source infrastructure for processing brain data at scale. Start building today.
2. Enable applications that restore mobility and create immersive neural experiences.
3. Developer-friendly APIs for neural prosthetics. Free tier available. Get started now.
4. Trusted by researchers and clinicians worldwide for neural interface applications.

## Budget Recommendations

### Starting Budget

- **Daily Budget**: $50-100
- **Bid Strategy**: Maximize Clicks (initially)
- **Target CPA**: $20-50 per sign-up

### Budget Allocation

- Brand Campaign: 20%
- Neural Prosthetics: 30%
- Developer Campaign: 30%
- Healthcare Campaign: 20%

## Tracking Success

### Key Metrics

1. **Sign-ups**: Track form submissions
2. **Demo Requests**: Track button clicks
3. **Documentation Views**: Track time on site
4. **API Key Generation**: Track as conversion

### Conversion Actions to Set Up

1. Newsletter Sign-up
2. Demo Request
3. Contact Form Submission
4. Account Creation
5. API Key Generation

## Next Steps

1. Complete account setup following steps 1-6
2. Add environment variables to Vercel
3. Implement tracking codes in the application
4. Create campaigns using the recommended structure
5. Monitor and optimize based on performance

## Support Resources

- Google Ads Help: https://support.google.com/google-ads
- API Documentation: https://developers.google.com/google-ads/api/docs/start
- NeuraScale Support: support@neurascale.io
