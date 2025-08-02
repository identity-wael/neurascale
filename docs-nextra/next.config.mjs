import nextra from 'nextra'

const withNextra = nextra({
  latex: true,
  search: true
})

export default withNextra({
  reactStrictMode: true
})
