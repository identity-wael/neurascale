# Deployment Instructions for Nextra Documentation

## Pre-Deployment Checklist

- [ ] All documentation migrated to MDX format
- [ ] Navigation structure configured in \_meta.json files
- [ ] Mermaid diagrams rendering correctly
- [ ] Local development server runs without errors
- [ ] All internal links working
- [ ] Images and assets copied over

## Deployment Steps

### 1. Prepare for Deployment

```bash
# Install dependencies
cd docs-nextra
pnpm install

# Test build locally
pnpm build

# Test production build
pnpm start
```

### 2. Push to GitHub

```bash
# Add all files
git add docs-nextra/

# Commit
git commit -m "feat: Migrate documentation to Nextra 4

- Complete architecture documentation with Mermaid diagrams
- Migrate existing Jekyll docs to MDX format
- Configure Vercel deployment
- Set up proper navigation structure
- Add dark mode and search functionality"

# Push branch
git push origin feat/nextra-documentation-migration
```

### 3. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import the GitHub repository
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `docs-nextra`
   - Build Command: `pnpm build` (auto-detected)
   - Output Directory: `.next` (auto-detected)
5. Deploy

### 4. Configure Custom Domain

**After successful deployment:**

1. In Vercel Dashboard → Project Settings → Domains
2. Add `docs.neurascale.io`
3. Vercel will show DNS configuration needed:
   ```
   Type: CNAME
   Name: docs
   Value: cname.vercel-dns.com
   ```

### 5. Update DNS Records

1. Log into your DNS provider
2. Find existing CNAME for docs.neurascale.io
3. Update the value from GitHub Pages to Vercel
4. Save changes

### 6. Monitor Migration

- [ ] Check Vercel deployment logs
- [ ] Verify SSL certificate issued
- [ ] Test docs.neurascale.io redirects properly
- [ ] Monitor for 404 errors
- [ ] Check all navigation links

### 7. Cleanup (After Verification)

**Only after 48 hours of stable operation:**

1. Remove CNAME file from `/docs-site`:

   ```bash
   git rm docs-site/CNAME
   git commit -m "chore: Remove GitHub Pages CNAME after Vercel migration"
   ```

2. Disable GitHub Pages:

   - Go to Settings → Pages
   - Change source to "None"
   - Save

3. Archive old documentation:
   ```bash
   git mv docs-site docs-site-archived
   git commit -m "chore: Archive old Jekyll documentation"
   ```

## Rollback Plan

If issues occur:

1. **Immediate Rollback:**

   - Remove custom domain from Vercel
   - DNS will revert to GitHub Pages (if not disabled yet)

2. **Fix Issues:**

   - Debug on Vercel preview URL
   - Fix any broken links or build errors
   - Redeploy

3. **Retry Migration:**
   - Follow steps above again

## Environment Variables

No environment variables needed for documentation site.

## Monitoring

- Vercel Analytics (automatically enabled)
- Google Analytics (if configured in theme.config.tsx)
- Check Vercel Functions logs for any API routes

## Support

- Vercel Support: https://vercel.com/support
- Nextra Issues: https://github.com/shuding/nextra/issues
- Internal: Create issue in main repository
