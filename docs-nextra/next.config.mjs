import nextra from 'nextra'

const withNextra = nextra({
  latex: true,
  defaultShowCopyCode: true,
  contentDirBasePath: "/docs",
})

/** @type {import('next').NextConfig} */
const nextConfig = withNextra({
  reactStrictMode: true,
  images: {
    domains: ['docs.neurascale.io'],
  },
  async redirects() {
    return [
      {
        source: '/getting-started',
        destination: '/docs/getting-started',
        permanent: true,
      },
      {
        source: '/docs/:path*',
        destination: '/docs/:path*',
        permanent: false,
      }
    ]
  }
})

export default nextConfig
