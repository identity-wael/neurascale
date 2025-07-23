'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { trackEvent } from '../../lib/google-analytics';
import { useGoogleAnalytics } from '../../hooks/useGoogleAnalytics';

export default function TestAnalyticsPage() {
  const { track } = useGoogleAnalytics();

  useEffect(() => {
    // Track page view (automatic with hook)
    console.log('GA4 Test Page Loaded');

    // Check if gtag is available
    if (typeof window !== 'undefined' && (window as any).gtag) {
      console.log('✅ Google Analytics is loaded!');
      console.log('GA4 Measurement ID:', process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID);
    } else {
      console.log('❌ Google Analytics not loaded yet');
    }
  }, []);

  const handleTestEvent = () => {
    trackEvent('test_button_click', {
      category: 'Test',
      label: 'GA4 Test Button',
      value: 1,
    });
    track('test_custom_event', {
      test_parameter: 'Hello GA4!',
    });
    console.log('Test events sent to GA4');
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Google Analytics 4 Test Page</h1>

        <div className="bg-gray-900 rounded-lg p-6 mb-8">
          <h2 className="text-2xl mb-4">GA4 Configuration</h2>
          <p className="mb-2">
            <strong>Measurement ID:</strong>{' '}
            {process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID || 'Not configured'}
          </p>
          <p className="mb-2">
            <strong>Status:</strong> Check browser console for GA4 loading status
          </p>
        </div>

        <div className="bg-gray-900 rounded-lg p-6 mb-8">
          <h2 className="text-2xl mb-4">Test Events</h2>
          <button
            onClick={handleTestEvent}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Send Test Event to GA4
          </button>
          <p className="mt-4 text-gray-400">
            Click the button and check GA4 Real-time reports to see the event
          </p>
        </div>

        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-2xl mb-4">How to Verify</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Open browser Developer Tools (F12)</li>
            <li>Check Console tab for GA4 loading messages</li>
            <li>
              Go to Network tab and filter by &quot;google-analytics&quot; or &quot;gtag&quot;
            </li>
            <li>Visit GA4 Real-time reports in Google Analytics dashboard</li>
            <li>You should see yourself as an active user</li>
          </ol>
        </div>

        <div className="mt-8">
          <Link href="/" className="text-blue-400 hover:underline">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
