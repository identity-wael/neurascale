---
layout: doc
title: Fix Google Maps
---

# Fix Google Maps "For Development Purposes Only" Watermark

## Common Causes and Solutions

### 1. **Check Billing Account** (Most Common)

The watermark appears when there's no active billing account linked to the project.

**To fix:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/billing)
2. Ensure the NeuraScale project has an active billing account
3. If not, click "Link a billing account" for the neurascale project

### 2. **Wait for Propagation**

API key changes can take 5-15 minutes to propagate globally.

**To verify:**

- Clear your browser cache
- Try incognito/private browsing mode
- Wait 15 minutes and refresh

### 3. **Verify Domain Restrictions**

Current restrictions for your API key:

- `https://neurascale.io/*`
- `https://*.neurascale.vercel.app/*`
- `http://localhost:3000/*`

**Check your current URL matches exactly** (including https vs http)

### 4. **Enable Additional APIs**

Sometimes the watermark appears if related APIs aren't enabled:

```bash
# Enable these additional APIs
gcloud services enable places-backend.googleapis.com --project=neurascale
gcloud services enable geocoding-backend.googleapis.com --project=neurascale
```

### 5. **Verify in Browser Console**

Open browser DevTools and check for errors:

```javascript
// Check if the API key is being passed correctly
console.log(window.google?.maps?.version);
```

### 6. **Quick Test**

Create a test file to verify the API key:

```html
<!doctype html>
<html>
  <head>
    <title>Maps API Test</title>
    <script>
      function initMap() {
        const map = new google.maps.Map(document.getElementById("map"), {
          center: { lat: 42.3601, lng: -71.0942 },
          zoom: 15,
        });
      }
    </script>
  </head>
  <body>
    <div id="map" style="height: 400px;"></div>
    <script
      async
      defer
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDV92WmqqGSQUiTiyZzgNVqElz-z82rC6w&callback=initMap"
    ></script>
  </body>
</html>
```

### 7. **Update API Key Restrictions**

If the issue persists, try temporarily removing restrictions:

```bash
gcloud alpha services api-keys update 824a507e-129e-4fb7-a74d-edb6340ed7b8 \
  --clear-restrictions \
  --project=neurascale
```

Then gradually add them back once it's working.

### 8. **Force Refresh in Vercel**

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Update `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` (just add a space and remove it)
3. Redeploy the application

## Most Likely Solution

**Enable billing for the neurascale project**. The "For development purposes only" watermark is Google's way of indicating that the Maps API is in development mode due to lack of billing.

To verify billing status:

1. Go to https://console.cloud.google.com/billing
2. Check if neurascale project has an active billing account
3. If not, link a billing account

Google provides $200/month free usage for Maps, which is more than enough for most websites.
