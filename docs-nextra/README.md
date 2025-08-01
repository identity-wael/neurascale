# NeuraScale Documentation (Nextra)

This is the new documentation site for NeuraScale, built with Nextra 4.

## Migration Status

✅ **Completed:**

- Nextra project setup
- Architecture documentation with Mermaid diagrams
- Navigation structure
- Core pages migrated to MDX
- Vercel configuration

🚧 **In Progress:**

- Migrating remaining documentation pages
- Setting up search functionality
- Dark mode configuration

📋 **TODO:**

- Deploy to Vercel
- Configure custom domain (docs.neurascale.io)
- Archive old Jekyll site

## Local Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

## Deployment

### Phase 1: Deploy to Vercel (Preview)

1. Push this branch to GitHub
2. Import project in Vercel dashboard
3. Configure build settings (already in vercel.json)
4. Deploy to preview URL

### Phase 2: Domain Configuration

1. Add docs.neurascale.io as custom domain in Vercel
2. Vercel will provide DNS records
3. Update DNS at your domain registrar
4. Wait for SSL certificate provisioning

### Phase 3: GitHub Pages Cleanup

**ONLY after Vercel deployment is verified:**

1. Remove CNAME file from /docs-site
2. Disable GitHub Pages in repo settings
3. Archive /docs-site to /docs-site-archived
4. Update README links

## DNS Migration Plan

**Current State:**

- docs.neurascale.io → GitHub Pages
- CNAME file in /docs-site

**Target State:**

- docs.neurascale.io → Vercel
- No GitHub Pages

**Migration Steps:**

1. Deploy to Vercel with preview URL
2. Test thoroughly on preview URL
3. Add custom domain in Vercel
4. Update DNS records (CNAME to cname.vercel-dns.com)
5. Monitor DNS propagation (24-48 hours)
6. Verify SSL certificate
7. Disable GitHub Pages

## Directory Structure

```
docs-nextra/
├── pages/
│   ├── index.mdx                    # Home page
│   ├── _meta.json                   # Navigation config
│   ├── architecture/
│   │   ├── overview.mdx             # Architecture overview
│   │   ├── system-components.mdx    # Detailed components
│   │   └── data-flow.mdx           # Data flow patterns
│   ├── documentation/
│   │   ├── getting-started.mdx
│   │   └── ...
│   └── console/
│       └── ...
├── components/
│   └── Mermaid.tsx                  # Mermaid diagram component
├── theme.config.tsx                 # Nextra theme configuration
├── next.config.mjs                  # Next.js configuration
└── vercel.json                      # Vercel deployment config
```

## Features

- 📚 Comprehensive documentation structure
- 🎨 Clean, modern design with Nextra
- 🔍 Built-in search functionality
- 🌓 Dark mode support
- 📊 Mermaid diagram support
- 📱 Mobile responsive
- ⚡ Fast page loads with Next.js
- 🔒 Secure headers configured

## Contributing

When adding new documentation:

1. Create MDX files in appropriate directories
2. Update \_meta.json for navigation
3. Use Nextra components for rich content
4. Test locally before pushing

## Support

For issues with documentation, please open an issue in the main repository.
