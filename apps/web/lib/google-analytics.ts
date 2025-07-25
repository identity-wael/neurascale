/**
 * Google Analytics 4 (GA4) Integration for NeuraScale
 * This module handles analytics tracking and reporting
 */

// GA4 Configuration
export const GA4_CONFIG = {
  MEASUREMENT_ID: process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID || '',
};

// Event categories for consistent tracking
export const GA_EVENTS = {
  // User engagement
  SIGN_UP: 'sign_up',
  LOGIN: 'login',
  LOGOUT: 'logout',

  // Content interaction
  PAGE_VIEW: 'page_view',
  SCROLL: 'scroll',
  CLICK: 'click',
  VIDEO_PLAY: 'video_play',
  VIDEO_COMPLETE: 'video_complete',

  // Form events
  FORM_START: 'form_start',
  FORM_SUBMIT: 'form_submit',
  CONTACT_FORM: 'contact_form',
  DEMO_REQUEST: 'demo_request',

  // Conversion events
  GENERATE_LEAD: 'generate_lead',
  DOWNLOAD: 'file_download',
  SHARE: 'share',

  // E-commerce (future)
  VIEW_ITEM: 'view_item',
  ADD_TO_CART: 'add_to_cart',
  PURCHASE: 'purchase',

  // Custom events
  API_KEY_GENERATED: 'api_key_generated',
  DOCUMENTATION_VIEW: 'documentation_view',
  CODE_COPY: 'code_copy',
} as const;

// Page categories for content grouping
export const PAGE_CATEGORIES = {
  HOME: 'home',
  MARKETING: 'marketing',
  DOCUMENTATION: 'documentation',
  DASHBOARD: 'dashboard',
  AUTH: 'authentication',
  RESOURCES: 'resources',
} as const;

/**
 * Initialize Google Analytics
 * Call this in _app.tsx or layout.tsx
 */
export function initializeGA() {
  if (typeof window === 'undefined' || !GA4_CONFIG.MEASUREMENT_ID) {
    return;
  }

  // Load gtag script
  const script = document.createElement('script');
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_CONFIG.MEASUREMENT_ID}`;
  script.async = true;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  function gtag(...args: any[]) {
    window.dataLayer.push(args);
  }

  gtag('js', new Date());
  gtag('config', GA4_CONFIG.MEASUREMENT_ID, {
    page_path: window.location.pathname,
    send_page_view: true,
    // Enhanced measurement
    cookie_flags: 'SameSite=None;Secure',
    // User properties
    custom_map: {
      dimension1: 'user_type',
      dimension2: 'account_tier',
    },
  });

  // Make gtag available globally
  (window as any).gtag = gtag;
}

/**
 * Track page views
 */
export function trackPageView(url: string, title?: string) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  gtag('event', 'page_view', {
    page_path: url,
    page_title: title || document.title,
    page_location: window.location.href,
  });
}

/**
 * Track custom events
 */
export function trackEvent(
  eventName: string,
  parameters?: {
    category?: string;
    label?: string;
    value?: number;
    [key: string]: any;
  }
) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  gtag('event', eventName, parameters);
}

/**
 * Track user interactions
 */
export function trackClick(
  elementName: string,
  elementType: 'button' | 'link' | 'image' | 'other',
  destination?: string
) {
  trackEvent('click', {
    element_name: elementName,
    element_type: elementType,
    link_url: destination,
  });
}

/**
 * Track form interactions
 */
export function trackFormStart(formName: string) {
  trackEvent('form_start', {
    form_name: formName,
    form_id: formName.toLowerCase().replace(/\s+/g, '_'),
  });
}

export function trackFormSubmit(formName: string, formValue?: number) {
  trackEvent('form_submit', {
    form_name: formName,
    form_id: formName.toLowerCase().replace(/\s+/g, '_'),
    value: formValue,
  });
}

/**
 * Track conversions
 */
export function trackConversion(conversionType: string, value?: number) {
  trackEvent('conversion', {
    conversion_type: conversionType,
    value: value || 0,
    currency: 'USD',
  });
}

/**
 * Track user properties
 */
export function setUserProperties(properties: {
  userId?: string;
  userType?: 'free' | 'pro' | 'enterprise';
  accountCreated?: string;
  [key: string]: any;
}) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  gtag('set', 'user_properties', properties);
}

/**
 * Track user ID for cross-device tracking
 */
export function setUserId(userId: string) {
  if (typeof window === 'undefined' || !(window as any).gtag) {
    return;
  }

  const gtag = (window as any).gtag;
  gtag('config', GA4_CONFIG.MEASUREMENT_ID, {
    user_id: userId,
  });
}

/**
 * Track scroll depth
 */
export function trackScrollDepth(percentage: number) {
  trackEvent('scroll', {
    percent_scrolled: percentage,
    page_path: window.location.pathname,
  });
}

/**
 * Track time on page
 */
export function trackTimeOnPage(seconds: number) {
  trackEvent('time_on_page', {
    engagement_time_msec: seconds * 1000,
    page_path: window.location.pathname,
  });
}

/**
 * Track outbound links
 */
export function trackOutboundLink(url: string) {
  trackEvent('click', {
    link_url: url,
    link_domain: new URL(url).hostname,
    link_classes: 'outbound',
    outbound: true,
  });
}

/**
 * Track downloads
 */
export function trackDownload(fileName: string, fileType: string) {
  trackEvent('file_download', {
    file_name: fileName,
    file_extension: fileType,
    link_text: fileName,
  });
}

/**
 * Track video engagement
 */
export function trackVideoPlay(videoTitle: string, videoUrl?: string) {
  trackEvent('video_play', {
    video_title: videoTitle,
    video_url: videoUrl,
  });
}

export function trackVideoProgress(videoTitle: string, percentage: number) {
  trackEvent('video_progress', {
    video_title: videoTitle,
    video_percent: percentage,
  });
}

export function trackVideoComplete(videoTitle: string) {
  trackEvent('video_complete', {
    video_title: videoTitle,
  });
}

/**
 * Enhanced Ecommerce (for future use)
 */
export function trackViewItem(item: {
  itemId: string;
  itemName: string;
  itemCategory?: string;
  itemBrand?: string;
  price?: number;
}) {
  trackEvent('view_item', {
    currency: 'USD',
    value: item.price || 0,
    items: [
      {
        item_id: item.itemId,
        item_name: item.itemName,
        item_category: item.itemCategory,
        item_brand: item.itemBrand,
        price: item.price,
        quantity: 1,
      },
    ],
  });
}

/**
 * Track exceptions/errors
 */
export function trackException(description: string, fatal: boolean = false) {
  trackEvent('exception', {
    description,
    fatal,
    page_path: window.location.pathname,
  });
}

/**
 * Track search queries
 */
export function trackSearch(searchTerm: string, searchCategory?: string) {
  trackEvent('search', {
    search_term: searchTerm,
    search_category: searchCategory,
  });
}

/**
 * Get analytics client ID for server-side tracking
 */
export function getClientId(): Promise<string> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined' || !(window as any).gtag) {
      resolve('');
      return;
    }

    const gtag = (window as any).gtag;
    gtag('get', GA4_CONFIG.MEASUREMENT_ID, 'client_id', (clientId: string) => {
      resolve(clientId);
    });
  });
}
