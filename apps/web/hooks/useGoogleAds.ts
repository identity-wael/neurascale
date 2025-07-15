/**
 * React Hook for Google Ads tracking
 */

import { useEffect, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import {
  initializeGoogleAds,
  trackPageView,
  trackConversion,
  trackFormSubmission,
  setUserData,
} from '@/lib/google-ads';

export function useGoogleAds() {
  const pathname = usePathname();

  // Initialize Google Ads on mount
  useEffect(() => {
    initializeGoogleAds();
  }, []);

  // Track page views for remarketing
  useEffect(() => {
    if (pathname) {
      trackPageView(pathname, document.title);
    }
  }, [pathname]);

  // Track sign up conversion
  const trackSignUp = useCallback((value?: number) => {
    trackConversion('SIGN_UP', value);
  }, []);

  // Track demo request
  const trackDemoRequest = useCallback((value?: number) => {
    trackConversion('DEMO_REQUEST', value);
  }, []);

  // Track contact form submission
  const trackContactForm = useCallback((value?: number) => {
    trackConversion('CONTACT_FORM', value);
  }, []);

  // Track API key generation
  const trackApiKeyGenerated = useCallback((value?: number) => {
    trackConversion('API_KEY_GENERATED', value);
  }, []);

  // Track documentation view
  const trackDocumentationView = useCallback((value?: number) => {
    trackConversion('DOCUMENTATION_VIEW', value);
  }, []);

  // Generic form tracking
  const trackForm = useCallback((formName: string, value?: number) => {
    trackFormSubmission(formName, value);
  }, []);

  // Set user data for enhanced conversions
  const updateUserData = useCallback((userData: Parameters<typeof setUserData>[0]) => {
    setUserData(userData);
  }, []);

  return {
    trackSignUp,
    trackDemoRequest,
    trackContactForm,
    trackApiKeyGenerated,
    trackDocumentationView,
    trackForm,
    updateUserData,
  };
}
