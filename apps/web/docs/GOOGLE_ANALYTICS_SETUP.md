# Google Analytics 4 Setup Guide for NeuraScale

## Overview

This guide helps you set up Google Analytics 4 (GA4) for NeuraScale to track user behavior, conversions, and site performance.

## Step 1: Create GA4 Property

1. **Go to Google Analytics**: https://analytics.google.com
2. **Create Property**:

   - Click Admin (gear icon) → Create Property
   - Property Name: NeuraScale
   - Time Zone: Your timezone
   - Currency: USD

3. **Business Information**:
   - Industry: Technology
   - Business Size: Select appropriate
   - Use Goals: All that apply

## Step 2: Set Up Data Stream

1. **Create Web Data Stream**:

   - Platform: Web
   - Website URL: https://neurascale.io
   - Stream Name: NeuraScale Production

2. **Get Measurement ID**:
   - Copy the `G-XXXXXXXXXX` ID
   - This is your `NEXT_PUBLIC_GA4_MEASUREMENT_ID`

## Step 3: Configure Enhanced Measurement

Enable all enhanced measurements:

- ✅ Page views
- ✅ Scrolls (90% depth)
- ✅ Outbound clicks
- ✅ Site search
- ✅ Video engagement
- ✅ File downloads
- ✅ Form interactions

## Step 4: Set Up Conversions

Mark these events as conversions:

### 1. **contact_form**

- When: User submits contact form
- Value: Lead value (optional)

### 2. **sign_up**

- When: User creates account
- Value: User lifetime value estimate

### 3. **demo_request**

- When: User requests demo
- Value: Demo value

### 4. **api_key_generated**

- When: User generates API key
- Value: Subscription value

## Step 5: Create Audiences

### 1. **Engaged Users**

- Conditions: Session duration > 60s OR 2+ page views

### 2. **Technical Users**

- Conditions: Viewed documentation OR generated API key

### 3. **High-Intent Users**

- Conditions: Viewed pricing OR contact page

### 4. **Returning Visitors**

- Conditions: 2+ sessions

## Step 6: Set Up Custom Dimensions

1. Go to Admin → Custom Definitions → Custom Dimensions
2. Create these dimensions:

### User-Scoped:

- **user_type**: free/pro/enterprise
- **account_created**: Date user signed up
- **api_usage**: Low/Medium/High

### Event-Scoped:

- **button_text**: Text of clicked button
- **form_name**: Name of submitted form
- **error_message**: Error details

## Step 7: Link with Google Ads

1. Admin → Product Links → Google Ads Linking
2. Link your Google Ads account
3. Enable:
   - ✅ Personalized advertising
   - ✅ Auto-tagging
   - ✅ Conversion import

## Step 8: Environment Variables

Add to Vercel:

```bash
NEXT_PUBLIC_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
```

## Step 9: Test Implementation

### Browser Console:

```javascript
// Check if GA4 is loaded
console.log(window.dataLayer);
console.log(window.gtag);
```

### GA4 DebugView:

1. Install GA Debugger Chrome Extension
2. Go to GA4 → Configure → DebugView
3. Navigate your site - events should appear

### Real-time Report:

1. Go to Reports → Real-time
2. You should see your own activity

## Step 10: Custom Reports

### Recommended Reports:

#### 1. **User Acquisition**

- Dimensions: Source/Medium, Landing Page
- Metrics: Users, Sessions, Engagement Rate

#### 2. **Content Performance**

- Dimensions: Page Path, Page Title
- Metrics: Views, Avg Time, Bounce Rate

#### 3. **Conversion Funnel**

- Events: page_view → form_start → form_submit
- Analyze drop-off rates

#### 4. **Technical Performance**

- Dimensions: Device Category, Browser
- Metrics: Page Load Time, Errors

## Event Tracking Reference

### Automatic Events (Enhanced Measurement):

- `page_view` - Every page navigation
- `scroll` - 90% scroll depth
- `click` - Outbound links
- `view_search_results` - Site search
- `file_download` - PDF, ZIP downloads

### Custom Events to Implement:

```javascript
// Sign Up
gtag('event', 'sign_up', {
  method: 'email',
});

// Contact Form
gtag('event', 'contact_form', {
  form_name: 'main_contact',
});

// API Key Generated
gtag('event', 'api_key_generated', {
  api_tier: 'free',
});

// Documentation View
gtag('event', 'documentation_view', {
  doc_category: 'getting_started',
  doc_page: 'installation',
});
```

## Best Practices

### 1. **Privacy Compliance**

- Add cookie consent banner
- Update privacy policy
- Honor user opt-outs

### 2. **Data Quality**

- Filter internal traffic (your IP)
- Exclude bot traffic
- Set up data retention (14 months recommended)

### 3. **Performance**

- Load GA4 asynchronously
- Use gtag events sparingly
- Batch events when possible

### 4. **Testing**

- Always test in DebugView first
- Verify conversions are firing
- Check data in Real-time reports

## Troubleshooting

### Events Not Showing:

1. Check Measurement ID is correct
2. Verify no ad blockers active
3. Check browser console for errors
4. Wait 24-48 hours for data

### Conversions Not Tracking:

1. Ensure event is marked as conversion
2. Check event parameters match
3. Verify no duplicate events

### Missing Data:

1. Check date range
2. Verify filters aren't excluding data
3. Ensure enhanced measurement is on

## Integration with Our Code

The implementation includes:

1. **Core Library** (`lib/google-analytics.ts`):

   - Event tracking functions
   - User property management
   - Enhanced ecommerce ready

2. **React Hook** (`hooks/useGoogleAnalytics.ts`):

   - Automatic page view tracking
   - Scroll depth tracking
   - Time on page tracking
   - Easy event helpers

3. **Setup Script** (`scripts/google/google_analytics_setup.py`):
   - View real-time data
   - Generate reports
   - Test configuration

## Next Steps

1. ✅ Create GA4 property and get Measurement ID
2. ✅ Add to Vercel environment variables
3. ✅ Deploy and verify in DebugView
4. ✅ Set up conversions and audiences
5. ✅ Create custom reports
6. ✅ Link with Google Ads for remarketing

## Resources

- [GA4 Documentation](https://developers.google.com/analytics/devguides/collection/ga4)
- [Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [GA4 Event Builder](https://ga-dev-tools.google/ga4/event-builder/)
- [DebugView Guide](https://support.google.com/analytics/answer/7201382)
