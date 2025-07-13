# NEURASCALE - Neural-Prosthetics Application Cloud

An open-source infrastructure for processing petabytes of brain data, enabling applications that restore mobility, unlock robotic control, and create immersive realities.

## 📁 Project Structure

```
neurascale/
├── apps/                       # Monorepo root
│   ├── web/                    # Next.js web application (Vercel deploys from here)
│   │   ├── app/
│   │   ├── components/
│   │   ├── public/
│   │   └── package.json
│   ├── packages/               # Shared packages
│   │   ├── ui/                 # Shared UI components
│   │   ├── config-typescript/  # TypeScript configs
│   │   └── config-tailwind/    # Tailwind configs
│   ├── package.json            # Workspace root (future)
│   ├── turbo.json              # Turborepo config (future)
│   └── pnpm-workspace.yaml     # PNPM workspaces (future)
├── backend/                    # Future backend services
├── infrastructure/             # Future IaC
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or pnpm

### Installation & Development

```bash
# Navigate to the web app
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 🎨 Features

- **3D Visualizations**: Neural processor and server rack animations using Three.js
- **Smooth Animations**: Framer Motion for fluid transitions
- **Loading Screen**: Professional loading experience
- **Responsive Design**: Works on all devices
- **Type Safety**: Full TypeScript support

## 🚢 Deployment

### Vercel Configuration
- **Root Directory**: `apps/web`
- **Framework Preset**: Next.js
- **Build & Output**: Auto-detected

## 🛠️ Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **3D Graphics**: Three.js, React Three Fiber
- **Animations**: Framer Motion, Lenis
- **Language**: TypeScript
- **Deployment**: Vercel

## 📦 Future Monorepo Setup

When ready to implement the full monorepo:

1. Add workspace configuration files to `apps/`
2. Move shared code to `apps/packages/`
3. Update imports to use workspace packages
4. Change Vercel root directory to `apps/`

## 👥 Team

Led by Rob Franklin (SVP, Blackrock Neurotech), Wael El Ghazzawi (CTO, Brain Finance), and a world-class team of engineers and researchers.

## 📄 License

[Your License]