/**
 * React Hook for Google Analytics tracking
 */

import { useEffect, useCallback, useRef } from 'react';
import { usePathname } from 'next/navigation';
import {
  initializeGA,
  trackPageView,
  trackEvent,
  trackClick,
  trackFormStart,
  trackFormSubmit,
  trackScrollDepth,
  trackTimeOnPage,
  setUserProperties,
  setUserId,
  GA_EVENTS,
} from '@/lib/google-analytics';

interface UseGoogleAnalyticsOptions {
  trackScrolling?: boolean;
  trackTimeOnPage?: boolean;
  userId?: string;
  userProperties?: Record<string, any>;
}

export function useGoogleAnalytics(options: UseGoogleAnalyticsOptions = {}) {
  const pathname = usePathname();
  const timeOnPageRef = useRef<number>(Date.now());
  const hasTrackedScrollRef = useRef<Set<number>>(new Set());

  // Initialize GA on mount
  useEffect(() => {
    initializeGA();
  }, []);

  // Track page views on route changes
  useEffect(() => {
    if (pathname) {
      trackPageView(pathname);
      // Reset tracking for new page
      timeOnPageRef.current = Date.now();
      hasTrackedScrollRef.current.clear();
    }
  }, [pathname]);

  // Set user ID if provided
  useEffect(() => {
    if (options.userId) {
      setUserId(options.userId);
    }
  }, [options.userId]);

  // Set user properties if provided
  useEffect(() => {
    if (options.userProperties) {
      setUserProperties(options.userProperties);
    }
  }, [options.userProperties]);

  // Track scroll depth
  useEffect(() => {
    if (!options.trackScrolling) return;

    const handleScroll = () => {
      const scrollPercentage = Math.round(
        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
      );

      // Track at 25%, 50%, 75%, and 100%
      const milestones = [25, 50, 75, 100];
      milestones.forEach((milestone) => {
        if (scrollPercentage >= milestone && !hasTrackedScrollRef.current.has(milestone)) {
          trackScrollDepth(milestone);
          hasTrackedScrollRef.current.add(milestone);
        }
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [options.trackScrolling]);

  // Track time on page
  useEffect(() => {
    if (!options.trackTimeOnPage) return;

    const interval = setInterval(() => {
      const timeOnPage = Math.round((Date.now() - timeOnPageRef.current) / 1000);
      trackTimeOnPage(timeOnPage);
    }, 30000); // Track every 30 seconds

    return () => clearInterval(interval);
  }, [options.trackTimeOnPage, pathname]);

  // Event tracking helpers
  const track = useCallback((eventName: string, parameters?: any) => {
    trackEvent(eventName, parameters);
  }, []);

  const trackButtonClick = useCallback((buttonName: string, destination?: string) => {
    trackClick(buttonName, 'button', destination);
  }, []);

  const trackLinkClick = useCallback((linkName: string, destination: string) => {
    trackClick(linkName, 'link', destination);
  }, []);

  const trackFormInteraction = useCallback(
    (formName: string, action: 'start' | 'submit', value?: number) => {
      if (action === 'start') {
        trackFormStart(formName);
      } else {
        trackFormSubmit(formName, value);
      }
    },
    []
  );

  // Common event tracking
  const trackSignUp = useCallback(
    (method?: string) => {
      track(GA_EVENTS.SIGN_UP, { method });
    },
    [track]
  );

  const trackLogin = useCallback(
    (method?: string) => {
      track(GA_EVENTS.LOGIN, { method });
    },
    [track]
  );

  const trackShare = useCallback(
    (method: string, contentType: string) => {
      track(GA_EVENTS.SHARE, { method, content_type: contentType });
    },
    [track]
  );

  const trackDownload = useCallback(
    (fileName: string) => {
      const extension = fileName.split('.').pop() || 'unknown';
      track(GA_EVENTS.DOWNLOAD, { file_name: fileName, file_extension: extension });
    },
    [track]
  );

  return {
    track,
    trackButtonClick,
    trackLinkClick,
    trackFormInteraction,
    trackSignUp,
    trackLogin,
    trackShare,
    trackDownload,
  };
}

/**
 * Hook for tracking component visibility
 */
export function useTrackVisibility(componentName: string, threshold: number = 0.5) {
  const hasTrackedRef = useRef(false);
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasTrackedRef.current) {
            trackEvent('view_item', {
              item_name: componentName,
              item_category: 'component',
            });
            hasTrackedRef.current = true;
          }
        });
      },
      { threshold }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [componentName, threshold]);

  return elementRef;
}
