import nextra from 'nextra'

const withNextra = nextra({
  // MDX options limited with Turbopack - avoid function-based plugins
})

export default withNextra({
  reactStrictMode: true,
  images: {
    domains: ['docs.neurascale.io'],
  }
})
