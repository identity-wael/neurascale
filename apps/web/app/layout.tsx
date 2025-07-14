import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '../components/AuthProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NEURASCALE - Neural-Prosthetics Application Cloud | Brain-Computer Interface Technology',
  description: 'Open-source infrastructure for processing petabytes of brain data. NEURASCALE enables neural prosthetics, brain-computer interfaces, and immersive reality applications through advanced neural processing technology.',
  keywords: 'brain-computer interface, BCI, neural prosthetics, neurotechnology, brain data processing, neural interfaces, MIT, neurascale, brain signals, neural computing',
  authors: [{ name: 'NEURASCALE Team' }],
  creator: 'NEURASCALE',
  publisher: 'NEURASCALE',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://neurascale.io'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'NEURASCALE - Neural-Prosthetics Application Cloud',
    description: 'Revolutionary open-source infrastructure for processing brain data, enabling neural prosthetics and brain-computer interfaces.',
    url: 'https://neurascale.io',
    siteName: 'NEURASCALE',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'NEURASCALE - Neural-Prosthetics Application Cloud',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'NEURASCALE - Neural-Prosthetics Application Cloud',
    description: 'Revolutionary open-source infrastructure for brain-computer interfaces and neural prosthetics.',
    images: ['/twitter-image.png'],
    creator: '@neurascale',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'NEURASCALE',
    description: 'Open-source neural-prosthetics application cloud for brain-computer interfaces',
    url: 'https://neurascale.io',
    logo: 'https://neurascale.io/logo.png',
    sameAs: [
      'https://github.com/identity-wael/neurascale',
      'https://twitter.com/neurascale',
      'https://linkedin.com/company/neurascale'
    ],
    address: {
      '@type': 'PostalAddress',
      addressLocality: 'Cambridge',
      addressRegion: 'MA',
      postalCode: '02139',
      addressCountry: 'US',
      streetAddress: 'MIT Campus'
    },
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'customer service',
      email: 'hello@neurascale.io',
      availableLanguage: 'English'
    },
    foundingDate: '2024',
    keywords: 'brain-computer interface, neural prosthetics, neurotechnology, brain data processing',
  }

  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
        <meta name="theme-color" content="#4185f4" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className={inter.className}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}
