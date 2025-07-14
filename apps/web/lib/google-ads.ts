/**
 * Google Ads API Integration for NeuraScale
 * This module handles Google Ads tracking and conversions
 */

// Google Ads Configuration
export const GOOGLE_ADS_CONFIG = {
  // Will be set from environment variables
  CONVERSION_ID: process.env.NEXT_PUBLIC_GOOGLE_ADS_CONVERSION_ID || '',
  DEVELOPER_TOKEN: process.env.GOOGLE_ADS_DEVELOPER_TOKEN || '',
  CLIENT_ID: process.env.GOOGLE_ADS_CLIENT_ID || '',
  CLIENT_SECRET: process.env.GOOGLE_ADS_CLIENT_SECRET || '',
  REFRESH_TOKEN: process.env.GOOGLE_ADS_REFRESH_TOKEN || '',
  CUSTOMER_ID: process.env.GOOGLE_ADS_CUSTOMER_ID || '',
};

// Conversion tracking events
export const CONVERSION_EVENTS = {
  SIGN_UP: 'sign_up',
  DEMO_REQUEST: 'demo_request',
  CONTACT_FORM: 'contact_form',
  API_KEY_GENERATED: 'api_key_generated',
  DOCUMENTATION_VIEW: 'documentation_view',
} as const;

/**
 * Initialize Google Ads tracking
 * Call this in _app.tsx or layout.tsx
 */
export function initializeGoogleAds() {
  if (typeof window === 'undefined' || !GOOGLE_ADS_CONFIG.CONVERSION_ID) {
    return;
  }

  // Load gtag script
  const script = document.createElement('script');
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GOOGLE_ADS_CONFIG.CONVERSION_ID}`;
  script.async = true;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  function gtag(...args: any[]) {
    window.dataLayer.push(args);
  }
  
  gtag('js', new Date());
  gtag('config', GOOGLE_ADS_CONFIG.CONVERSION_ID);

  // Make gtag available globally
  (window as any).gtag = gtag;
}

/**
 * Track a conversion event
 */
export function trackConversion(
  eventName: keyof typeof CONVERSION_EVENTS,
  value?: number,
  currency: string = 'USD'
) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    console.warn('Google Ads not initialized');
    return;
  }

  const gtag = (window as any).gtag;
  
  // Track the conversion
  gtag('event', 'conversion', {
    send_to: `${GOOGLE_ADS_CONFIG.CONVERSION_ID}/${eventName}`,
    value: value || 0,
    currency: currency,
  });

  // Also track as a standard event for Google Analytics
  gtag('event', eventName, {
    value: value || 0,
    currency: currency,
  });
}

/**
 * Track page view for remarketing
 */
export function trackPageView(pagePath: string, pageTitle: string) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  
  gtag('event', 'page_view', {
    page_path: pagePath,
    page_title: pageTitle,
    send_to: GOOGLE_ADS_CONFIG.CONVERSION_ID,
  });
}

/**
 * Track form submissions
 */
export function trackFormSubmission(formName: string, formValue?: number) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  
  gtag('event', 'generate_lead', {
    currency: 'USD',
    value: formValue || 0,
    form_name: formName,
  });
}

/**
 * Enhanced Conversion Data
 * Send hashed user data for better conversion tracking
 */
export function setUserData(userData: {
  email?: string;
  phone?: string;
  firstName?: string;
  lastName?: string;
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
}) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  
  // Google Ads will automatically hash this data
  gtag('set', 'user_data', {
    email: userData.email,
    phone_number: userData.phone,
    address: {
      first_name: userData.firstName,
      last_name: userData.lastName,
      city: userData.city,
      region: userData.state,
      country: userData.country,
      postal_code: userData.postalCode,
    },
  });
}

/**
 * Track custom conversions with labels
 */
export function trackCustomConversion(
  conversionLabel: string,
  conversionValue?: number,
  transactionId?: string
) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  
  gtag('event', 'conversion', {
    send_to: `${GOOGLE_ADS_CONFIG.CONVERSION_ID}/${conversionLabel}`,
    value: conversionValue || 0,
    currency: 'USD',
    transaction_id: transactionId,
  });
}