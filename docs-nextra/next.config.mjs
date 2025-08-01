import nextra from 'nextra'

const withNextra = nextra()

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    turbo: {
      resolveAlias: {
        'next-mdx-import-source-file': './mdx-components.tsx',
      },
    },
  },
  images: {
    domains: ['docs.neurascale.io'],
  },
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
  async redirects() {
    return [
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
  }
}

export default withNextra(nextConfig)
