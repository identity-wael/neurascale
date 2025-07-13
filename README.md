# Neurascale

A neural data cloud platform built with Next.js and a Turborepo monorepo architecture.

## 🏗️ Project Structure

```
neurascale/
├── apps/                       # Turborepo monorepo root
│   ├── web/                    # Next.js web application
│   ├── packages/
│   │   └── ui/                 # Shared UI components
│   ├── package.json            # Workspace root
│   ├── turbo.json              # Turborepo configuration
│   └── [future apps]           # iOS, Android, admin dashboard, etc.
└── [other project components]  # Infrastructure, backend services, etc.
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm 9+

### Installation & Development

1. Navigate to the monorepo directory:
```bash
cd apps
```

2. Install dependencies for all workspaces:
```bash
npm install
```

3. Start development server:
```bash
# Start all apps in development mode
npm run dev

# Or start just the web app
cd web
npm run dev
```

The web application will be available at `http://localhost:3000`.

## 💻 Available Scripts

From the monorepo root (`apps/`):

- `npm run dev` - Start development servers for all apps
- `npm run build` - Build all apps and packages  
- `npm run lint` - Lint all packages
- `npm run type-check` - Run TypeScript checks

## 📦 Packages

### @neurascale/ui
Shared UI components library with Button, Card, and other reusable components.

## 🔧 Adding New Apps

To add a new application (iOS, Android, admin dashboard, etc.):

1. Create a new directory in `apps/`
2. Add package.json with workspace dependency on shared packages
3. Update root turbo.json pipeline if needed

## 🔧 Adding New Packages

To add a new shared package:

1. Create directory in `apps/packages/`
2. Add package.json with appropriate exports
3. Add TypeScript configuration if needed

## 🚀 Deployment

### Vercel (Web App)
The web application is deployed via Vercel with the following configuration:
- **Root Directory**: `apps/web`
- **Build Command**: `npm run build`
- **Framework Preset**: Next.js

### Other Deployments
Future iOS and Android apps will have their own deployment configurations.

## 🏛️ Architecture

This project uses a **hybrid monorepo approach**:
- **Turborepo monorepo** in `apps/` for client applications and shared packages
- **Project root** for infrastructure, backend services, and other components
- **Shared packages** for UI components, utilities, and common code

This allows for:
- Efficient code sharing between client applications
- Independent deployment of different app types
- Flexible project structure for various components
- Scalable development workflow