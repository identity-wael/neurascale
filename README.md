# NEURASCALE - Neural-Prosthetics Application Cloud

[![CodeQL](https://github.com/identity-wael/neurascale/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/identity-wael/neurascale/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/identity-wael/neurascale/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/identity-wael/neurascale/actions/workflows/dependency-review.yml)
[![Neon Database](https://img.shields.io/badge/Database-Neon-00E599)](https://neon.tech)
[![Sanity CMS](https://img.shields.io/badge/CMS-Sanity-F03E2F)](https://sanity.io)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An open-source infrastructure for processing petabytes of brain data, enabling applications that restore mobility, unlock robotic control, and create immersive realities.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/identity-wael/neurascale.git
cd neurascale

# Navigate to the web app
cd apps/web

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

Visit `http://localhost:3000` to see the application.

## 📁 Project Structure

```
neurascale/
├── apps/                       # Monorepo root
│   ├── web/                    # Next.js web application
│   │   ├── app/               # App router pages
│   │   ├── components/        # React components
│   │   ├── src/               # Source code
│   │   │   ├── lib/          # Utilities and clients
│   │   │   ├── sanity/       # Sanity schemas
│   │   │   └── contexts/     # React contexts
│   │   ├── scripts/          # Migration and utility scripts
│   │   └── package.json
│   └── packages/              # Shared packages (future)
├── console/                   # NeuraScale Console
├── .github/                   # GitHub workflows
│   ├── workflows/            # CI/CD pipelines
│   └── scripts/              # Workflow scripts
├── docs/                      # Documentation
└── README.md                  # This file
```

## 🛠️ Technology Stack

- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Database**: [Neon](https://neon.tech) (Serverless Postgres)
- **CMS**: [Sanity](https://sanity.io) (Headless CMS)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **3D Graphics**: [Three.js](https://threejs.org/), React Three Fiber
- **Animations**: [Framer Motion](https://www.framer.com/motion/), Lenis
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Deployment**: [Vercel](https://vercel.com)

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in `apps/web/` with:

```bash
# Sanity Configuration (Required)
NEXT_PUBLIC_SANITY_PROJECT_ID=vvsy01fb
NEXT_PUBLIC_SANITY_DATASET=production
NEXT_PUBLIC_SANITY_API_VERSION=2024-01-01

# Sanity API Token (Optional - for write operations)
SANITY_API_TOKEN=your-token-here

# Google Services (Optional)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-api-key
NEXT_PUBLIC_GA4_MEASUREMENT_ID=your-measurement-id

# Email Configuration (Optional)
EMAIL_USER=your-email@gmail.com
# EMAIL_PASS - See documentation for app-specific password setup
```

### Vercel Deployment

1. **Import Project**: Connect your GitHub repository to Vercel
2. **Configure Build**:
   - Root Directory: `apps/web`
   - Framework Preset: Next.js
   - Build Command: Auto-detected
3. **Environment Variables**: Add all required variables in Vercel project settings

## 📊 Content Management (Sanity CMS)

### Accessing Sanity Studio

- **Local**: `http://localhost:3000/studio`
- **Production**: `https://your-domain.vercel.app/studio`

### Content Structure

- **Hero**: Landing page hero section
- **Vision**: Mission and vision content
- **Problem**: Problem statement and solutions
- **Roadmap**: Development timeline
- **Team**: Team member profiles
- **Resources**: Documentation and resources
- **Contact**: Contact information

### Managing Content

1. Access Studio at `/studio`
2. Log in with your Sanity account
3. Edit content in real-time
4. Changes reflect immediately

## 🗄️ Database Management (Neon)

### Branch Strategy

- **Production**: Main database branch
- **Preview**: Automatic branches for PRs
- **Development**: Local development branch

### Automatic PR Branches

When you create a PR:

1. Neon automatically creates a database branch
2. Branch name: `preview/pr-{number}-{branch-name}`
3. Isolated testing environment
4. Deleted when PR is closed (not merged)

### Database Migrations

```bash
# Run migrations
npm run db:migrate

# Create new migration
npm run db:migrate:create
```

## 🚢 Deployment Pipeline

### GitHub Actions Workflows

1. **CodeQL Analysis**: Security scanning
2. **Dependency Review**: Vulnerability checks
3. **Neon Branch Management**:
   - Creates branches for PRs
   - Cleans up old branches weekly
4. **Vercel Deployment**: Automatic deployments

### Manual Deployment

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel
```

## 📖 Documentation

### Core Documentation

- [Sanity Integration Guide](docs/SANITY_INTEGRATION.md) - Headless CMS setup and content management
- [Neon Database Setup](docs/NEON_DATABASE.md) - Database branching and management
- [Environment Variables](docs/ENVIRONMENT_VARIABLES.md) - Complete configuration reference
- [Deployment Guide](docs/DEPLOYMENT.md) - Vercel deployment and optimization
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project
- [Security Policy](SECURITY.md) - Security practices and vulnerability reporting

### Google Services Integration

- [Google Analytics Setup](docs/GOOGLE_ANALYTICS_SETUP.md) - GA4 configuration and tracking
- [Google Ads Setup](docs/GOOGLE_ADS_SETUP.md) - Ads API integration and campaign management
- [Google Maps Fix](docs/fix-google-maps.md) - Troubleshooting Maps API issues

### Console Application

- [Console README](console/README.md) - NeuraScale Console documentation
- [Firebase Setup](console/FIREBASE_SETUP.md) - Firebase authentication guide
- [Infrastructure Guide](console/infrastructure/README.md) - Terraform and GCP setup

## 🧪 Development

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Type checking
npm run type-check
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

### Pre-commit Hooks

The project uses pre-commit hooks for:

- Code formatting (Prettier)
- Linting (ESLint)
- Type checking
- Security scanning

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👥 Team

### Leadership & Engineering Excellence

**Wael El Ghazzawi** - _CTO, Financial Technology_
Brain Finance

**Ron Lehman** - _CEO, Geographic Information System_
RYKER

**Donald Woodruff** - _Director of Technology, Cloud Solutions_
Lumen Technologies

**Jason Franklin** - _CITO, E-Retail_
American Furniture Warehouse

**Vincent Liu** - _VP Engineering, HealthCare_
CuraeSoft Inc

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Website](https://neurascale.com)
- [Documentation](https://docs.neurascale.io)
- [Sanity Studio](https://neurascale.com/studio)
- [GitHub](https://github.com/identity-wael/neurascale)

---

Built with ❤️ by the NeuraScale team
