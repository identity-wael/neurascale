# NeuraScale Developer Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Development Environment](#development-environment)
4. [Architecture Overview](#architecture-overview)
5. [API Reference](#api-reference)
6. [Best Practices](#best-practices)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## Introduction

Welcome to the NeuraScale developer guide. This comprehensive guide will help you build applications on our neural cloud platform.

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- pnpm 9.x or higher
- Git
- A code editor (VS Code recommended)
- Basic knowledge of TypeScript and React

### Initial Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/identity-wael/neurascale.git
   cd neurascale
   ```

2. **Install Dependencies**

   ```bash
   pnpm install
   ```

3. **Environment Configuration**

   ```bash
   cd apps/web
   cp .env.example .env.local
   ```

4. **Configure Environment Variables**
   Edit `.env.local` with your credentials:

   ```env
   # Required
   NEXT_PUBLIC_SANITY_PROJECT_ID=your_project_id
   NEXT_PUBLIC_SANITY_DATASET=production
   DATABASE_URL=your_neon_database_url

   # Optional
   NEXT_PUBLIC_GA4_MEASUREMENT_ID=your_ga_id
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_maps_key
   ```

5. **Start Development Server**
   ```bash
   pnpm dev
   ```

## Development Environment

### Recommended VS Code Extensions

- ESLint
- Prettier
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- Prisma
- GitLens

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

## Architecture Overview

### Frontend Architecture

```
apps/web/
├── app/                    # Next.js App Router
│   ├── (routes)/          # Page routes
│   ├── api/               # API endpoints
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── layout/           # Layout components
│   ├── sections/         # Page sections
│   ├── ui/              # UI components
│   └── visuals/         # 3D visualizations
├── hooks/                # Custom React hooks
├── lib/                  # Utilities
└── types/               # TypeScript types
```

### Component Structure

Each component follows this pattern:

```typescript
// components/example/ExampleComponent.tsx
import { FC } from 'react';

interface ExampleComponentProps {
  title: string;
  description?: string;
}

const ExampleComponent: FC<ExampleComponentProps> = ({
  title,
  description
}) => {
  return (
    <div className="example-component">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
};

export default ExampleComponent;
```

## API Reference

### REST API Endpoints

#### Authentication

```typescript
// POST /api/auth/login
{
  email: string;
  password: string;
}

// POST /api/auth/signup
{
  email: string;
  password: string;
  name: string;
}

// POST /api/auth/logout
// No body required
```

#### Contact Form

```typescript
// POST /api/contact
{
  name: string;
  email: string;
  organization?: string;
  subject: string;
  message: string;
}
```

### Database Schema

Using Prisma ORM:

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  password  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

### Sanity CMS Integration

Fetch content:

```typescript
import { sanityFetch } from "@/lib/sanity.client";

const content = await sanityFetch<ContentType>({
  query: `*[_type == "hero"][0]`,
  tags: ["hero"],
});
```

## Best Practices

### Code Style

1. **TypeScript First**

   - Use TypeScript for all new code
   - Define interfaces for all props
   - Avoid `any` type

2. **Component Guidelines**

   - Keep components small and focused
   - Use composition over inheritance
   - Implement proper error boundaries

3. **Performance**
   - Use dynamic imports for large components
   - Implement proper memoization
   - Optimize images with Next.js Image

### State Management

```typescript
// Use React Context for global state
import { createContext, useContext } from "react";

const AppContext = createContext<AppState | null>(null);

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within AppProvider");
  }
  return context;
};
```

### Error Handling

```typescript
// Consistent error handling
try {
  const result = await fetchData();
  return { data: result, error: null };
} catch (error) {
  console.error("Error fetching data:", error);
  return { data: null, error: error.message };
}
```

## Testing

### Unit Testing

```typescript
// __tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import Button from '@/components/ui/Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
```

### Integration Testing

```typescript
// __tests__/api/contact.test.ts
import { POST } from "@/app/api/contact/route";

describe("/api/contact", () => {
  it("sends email successfully", async () => {
    const request = new Request("http://localhost:3000/api/contact", {
      method: "POST",
      body: JSON.stringify({
        name: "Test User",
        email: "test@example.com",
        subject: "Test",
        message: "Test message",
      }),
    });

    const response = await POST(request);
    expect(response.status).toBe(200);
  });
});
```

## Deployment

### Vercel Deployment

1. **Connect Repository**

   - Link GitHub repo to Vercel
   - Set root directory to `apps/web`

2. **Environment Variables**

   - Add all variables from `.env.local`
   - Use Vercel's environment variable UI

3. **Build Settings**
   - Framework Preset: Next.js
   - Build Command: `pnpm build`
   - Output Directory: `.next`

### Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Sanity content published
- [ ] SSL certificates valid
- [ ] Monitoring configured
- [ ] Error tracking enabled
- [ ] Performance optimized
- [ ] Security headers set

## Troubleshooting

### Common Issues

#### Module Not Found

```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### TypeScript Errors

```bash
# Check types
pnpm typecheck

# Generate Prisma types
pnpm db:generate
```

#### Build Failures

```bash
# Clean build
rm -rf .next
pnpm build
```

### Debug Mode

Enable debug logging:

```typescript
// lib/debug.ts
export const debug =
  process.env.NODE_ENV === "development" ? console.log : () => {};
```

### Performance Profiling

Use React DevTools Profiler:

1. Install React Developer Tools
2. Open Profiler tab
3. Record performance
4. Analyze flame graph

## Advanced Topics

### Custom Hooks

```typescript
// hooks/useNeuralData.ts
export function useNeuralData(sensorId: string) {
  const [data, setData] = useState<NeuralData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const subscription = subscribeToNeuralData(sensorId, (newData) => {
      setData(newData);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [sensorId]);

  return { data, loading };
}
```

### WebGL Integration

```typescript
// components/visuals/NeuralVisualization.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

export default function NeuralVisualization({ data }) {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <NeuralMesh data={data} />
      <OrbitControls />
    </Canvas>
  );
}
```

### Real-time Updates

```typescript
// lib/realtime.ts
import { io } from "socket.io-client";

export const socket = io(process.env.NEXT_PUBLIC_SOCKET_URL, {
  autoConnect: false,
});

export function subscribeToUpdates(callback: (data: any) => void) {
  socket.on("update", callback);
  return () => socket.off("update", callback);
}
```

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Three.js](https://threejs.org/docs)

---

_Need help? Contact us at developer@neurascale.io_
