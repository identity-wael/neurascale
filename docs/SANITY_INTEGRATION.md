# Sanity CMS Integration Guide

This guide covers the Sanity CMS integration in the NeuraScale project, including setup, content management, and development workflows.

## Overview

Sanity is our headless CMS that powers all dynamic content on the NeuraScale website. It provides:

- 🎨 Visual content editing interface
- 🔄 Real-time content updates
- 📱 Responsive preview
- 🔐 Role-based access control
- 📊 Content versioning

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Sanity.io     │────▶│  Next.js App │────▶│   Browser   │
│   (Content)     │     │  (SSR/SSG)   │     │  (Client)   │
└─────────────────┘     └──────────────┘     └─────────────┘
         │                      │
         │                      ▼
         │              ┌──────────────┐
         └─────────────▶│ Sanity Studio│
                        │  (/studio)   │
                        └──────────────┘
```

## Content Structure

### Schemas

All content schemas are defined in `apps/web/src/sanity/schemas/`:

```
schemas/
├── hero.ts         # Landing page hero section
├── vision.ts       # Vision and mission content
├── problem.ts      # Problem statement
├── roadmap.ts      # Development timeline
├── team.ts         # Team members
├── resources.ts    # Resources and documentation
├── contact.ts      # Contact information
└── index.ts        # Schema exports
```

### Content Types

#### Hero Section

```typescript
{
  title: string;
  subtitle: string;
  ctaText: string;
  ctaLink: string;
}
```

#### Vision Section

```typescript
{
  sectionHeader: string;
  title: string;
  mainStat: string;
  mainStatDescription: text;
  stat1Value: string;
  stat1Label: string;
  stat2Value: string;
  stat2Label: string;
  solutionTitle: string;
  solutionPoints: array;
  solutionDescription: text;
}
```

## Setup Instructions

### 1. Sanity Project Setup

The project is already configured with Sanity project ID `vvsy01fb`. To set up your own:

```bash
# Install Sanity CLI globally
npm install -g @sanity/cli

# Initialize new project (optional)
sanity init

# Deploy GraphQL API (optional)
sanity graphql deploy
```

### 2. Environment Configuration

Add to `.env.local`:

```bash
# Required
NEXT_PUBLIC_SANITY_PROJECT_ID=vvsy01fb
NEXT_PUBLIC_SANITY_DATASET=production
NEXT_PUBLIC_SANITY_API_VERSION=2024-01-01

# Optional (for write operations)
SANITY_API_TOKEN=your-token-here
```

### 3. API Token Creation

For content migrations or programmatic updates:

1. Go to https://sanity.io/manage/project/vvsy01fb/api
2. Create new token with "Editor" permissions
3. Add to `.env.local` as `SANITY_API_TOKEN`

## Development Workflow

### Running Sanity Studio

```bash
# Development
npm run dev
# Visit http://localhost:3000/studio

# Production
# Visit https://your-domain.com/studio
```

### Content Fetching

Content is fetched server-side using GROQ queries:

```typescript
// apps/web/src/lib/sanity.queries.ts
export const PAGE_CONTENT_QUERY = groq`{
  "hero": *[_type == "hero"][0],
  "vision": *[_type == "vision"][0],
  "problem": *[_type == "problem"][0],
  // ... other sections
}`;
```

### Using Content in Components

```typescript
// Server Component
import { getPageContent } from '@/src/lib/sanity.queries'

export default async function Page() {
  const content = await getPageContent()
  return <ClientComponent content={content} />
}

// Client Component
import { useContent } from '@/src/contexts/ContentContext'

export default function Section() {
  const { hero, vision } = useContent()
  return <div>{hero?.title}</div>
}
```

## Content Migration

### Running Migrations

```bash
# Migrate all content
cd apps/web
npx tsx scripts/migrate-all-content.ts

# Check migration status
npx tsx scripts/check-sanity-content.ts
```

### Creating New Migrations

```typescript
// scripts/migrate-new-section.ts
import { createClient } from "@sanity/client";

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: "production",
  apiVersion: "2024-01-01",
  token: process.env.SANITY_API_TOKEN,
  useCdn: false,
});

const content = {
  _type: "section",
  _id: "section-main",
  // ... your content
};

await client.createOrReplace(content);
```

## Best Practices

### 1. Schema Design

- Use descriptive field names
- Add validation rules
- Provide helpful descriptions
- Use proper field types

```typescript
defineField({
  name: "title",
  title: "Title",
  type: "string",
  validation: (Rule) => Rule.required().max(80),
  description: "Main heading (max 80 characters)",
});
```

### 2. Content Modeling

- Keep documents focused and single-purpose
- Use references for relationships
- Avoid deeply nested structures
- Use arrays for repeating content

### 3. Performance

- Use ISR (Incremental Static Regeneration)
- Enable CDN in production
- Implement proper caching
- Optimize GROQ queries

```typescript
// Enable CDN for production
const client = createClient({
  // ...
  useCdn: process.env.NODE_ENV === "production",
});
```

### 4. Security

- Never expose write tokens in client code
- Use environment variables
- Implement CORS properly
- Regular token rotation

## Troubleshooting

### Common Issues

#### 1. "Configuration must contain projectId"

- Ensure environment variables are set
- Check `.env.local` file exists
- Verify Vercel environment variables

#### 2. "Missing keys in arrays"

- Add `_key` property to array items
- Use unique identifiers

```typescript
solutionPoints: [
  { _key: "point1", text: "...", highlight: "..." },
  { _key: "point2", text: "...", highlight: "..." },
];
```

#### 3. Studio not loading

- Check browser console for errors
- Verify project ID and dataset
- Clear browser cache
- Check CORS settings

### Debug Commands

```bash
# Test Sanity connection
npx tsx scripts/test-sanity-connection.ts

# List all documents
npx tsx scripts/check-sanity-content.ts

# Check specific document
curl "https://vvsy01fb.api.sanity.io/v2024-01-01/data/query/production?query=*[_id=='hero-main']"
```

## Advanced Topics

### Custom Input Components

```typescript
// Create custom input component
export default {
  name: "colorPicker",
  title: "Color",
  type: "string",
  inputComponent: ColorPickerInput,
};
```

### Webhooks

Set up webhooks for cache invalidation:

```typescript
// api/revalidate.ts
export async function POST(req: Request) {
  const { _type } = await req.json();

  // Revalidate specific paths
  revalidatePath("/");

  return Response.json({ revalidated: true });
}
```

### Preview Mode

Enable live preview for editors:

```typescript
// app/api/preview/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get("secret");

  if (secret !== process.env.SANITY_PREVIEW_SECRET) {
    return new Response("Invalid token", { status: 401 });
  }

  // Enable preview mode
  // Redirect to preview URL
}
```

## Resources

- [Sanity Documentation](https://www.sanity.io/docs)
- [GROQ Query Reference](https://www.sanity.io/docs/groq)
- [Next.js + Sanity Guide](https://www.sanity.io/guides/nextjs-app-router)
- [Sanity Studio Customization](https://www.sanity.io/docs/studio)
