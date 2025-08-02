import nextra from 'nextra'

const withNextra = nextra({
  latex: true,
  flexsearch: {
    codeblocks: false
  }
})

export default withNextra({
  reactStrictMode: true
})
