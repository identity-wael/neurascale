# Documentation Subdomain Setup

Since cross-origin rewrites don't work with Vercel (they trigger authentication), we need to use a subdomain approach.

## Setup Instructions

### 1. Add Custom Domain in Vercel

1. Go to your docs-nextra project in Vercel
2. Go to Settings → Domains
3. Add `docs.neurascale.io`

### 2. Configure DNS

Add a CNAME record in your DNS provider:

```
Type: CNAME
Name: docs
Value: cname.vercel-dns.com
TTL: 3600 (or your provider's default)
```

### 3. Wait for DNS Propagation

DNS changes can take up to 48 hours to propagate, but usually complete within a few minutes.

## Alternative: Redirect from /docs

If you want neurascale.io/docs to redirect to docs.neurascale.io, add this to apps/web:

```typescript
// In app/docs/route.ts
import { redirect } from "next/navigation";

export function GET() {
  redirect("https://docs.neurascale.io");
}
```

## Benefits of Subdomain Approach

- Clean separation between main site and docs
- No authentication issues
- Better performance (direct routing)
- Easier to manage and deploy independently
- Standard practice for documentation sites
