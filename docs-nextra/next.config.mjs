/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['docs.neurascale.io'],
  },
  async redirects() {
    return [
      // Preserve existing URLs
      {
        source: '/getting-started',
        destination: '/docs/getting-started',
        permanent: true,
      },
      {
        source: '/docs/:path*',
        destination: '/documentation/:path*',
        permanent: true,
      }
    ]
  },
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx']
}

export default nextConfig
