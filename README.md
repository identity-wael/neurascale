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

### Environment Variables Configuration

The application requires the following environment variables:
- `EMAIL_USER` - Email address for sending contact form messages
- `EMAIL_PASS` - Email password/app password
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` - Google Maps API key

#### Option 1: Vercel Environment Variables (Recommended for Production)

**Best for:** Production deployment, easier management, automatic integration

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Navigate to Settings → Environment Variables
4. Add the following variables:
   ```
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```
5. Choose the environments (Production, Preview, Development)
6. Save and redeploy

**Advantages:**
- Automatic injection into your app during build/runtime
- Secure storage with encryption
- Easy to update without code changes
- Different values for different environments
- No risk of accidentally committing secrets

#### Option 2: GitHub Secrets (For CI/CD)

**Best for:** GitHub Actions, automated testing, build processes

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add new repository secrets:
   ```
   EMAIL_USER
   EMAIL_PASS
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
   ```
4. Update your Vercel deployment to use GitHub secrets:

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          EMAIL_USER: ${{ secrets.EMAIL_USER }}
          EMAIL_PASS: ${{ secrets.EMAIL_PASS }}
          NEXT_PUBLIC_GOOGLE_MAPS_API_KEY: ${{ secrets.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY }}
        run: |
          npm i -g vercel
          vercel --prod --token=$VERCEL_TOKEN
```

#### Option 3: Local Development

For local development, create `.env.local`:
```bash
cp apps/web/.env.local.example apps/web/.env.local
```

Then add your credentials to `.env.local`.

### Recommended Approach

**Use Vercel Environment Variables** for the following reasons:
1. **Seamless Integration** - Vercel automatically injects env vars during build
2. **Security** - Values are encrypted and never exposed in logs
3. **Easy Management** - Update values without code changes
4. **Environment-specific** - Different values for production/preview/development
5. **No Additional Setup** - Works out of the box with your existing Vercel deployment

### Setting Up Email Credentials

For Gmail users:
1. Enable 2-factor authentication
2. Generate an App Password at: https://myaccount.google.com/apppasswords
3. Use the app password (not your regular password) as `EMAIL_PASS`

### Setting Up Google Maps

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Maps JavaScript API"
4. Create credentials (API Key)
5. Restrict the key to your domains:
   - `localhost:3000` for development
   - `your-domain.vercel.app` for production
   - Your custom domain if applicable

**Note**: Both the contact form and map will work in development mode with warnings if credentials are not configured.

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

### Leadership & Engineering Excellence

**Rob Franklin** - *SVP, Brain Computer Interface*  
Blackrock Neurotech

**Wael El Ghazzawi** - *CTO, Financial Technology*  
Brain Finance

**Ron Lehman** - *CEO, Geographic Information System*  
RYKER

**Donald Woodruff** - *Director of Technology, Cloud Solutions*  
Lumen Technologies

**Jason Franklin** - *CITO, E-Retail*  
American Furniture Warehouse

**Vincent Liu** - *VP Engineering, HealthCare*  
CuraeSoft Inc

Our world-class team brings together expertise from brain-computer interfaces, financial technology, cloud infrastructure, retail systems, and healthcare engineering to create the future of neural-prosthetics applications.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.