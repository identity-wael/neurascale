import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '../components/AuthProvider';
import { SpeedInsights } from '@vercel/speed-insights/next';
import { Analytics } from '@vercel/analytics/react';
import Script from 'next/script';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'NEURASCALE - Neural-Prosthetics Application Cloud',
  description:
    'Open-source infrastructure for processing petabytes of brain data, enabling applications that restore mobility, unlock robotic control, and create immersive realities.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const googleAdsId = process.env.NEXT_PUBLIC_GOOGLE_ADS_CONVERSION_ID;
  
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
          <SpeedInsights />
          <Analytics />
        </AuthProvider>
        
        {/* Google Ads Conversion Tracking */}
        {googleAdsId && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${googleAdsId}`}
              strategy="afterInteractive"
            />
            <Script id="google-ads" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${googleAdsId}');
              `}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
