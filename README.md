# NEURASCALE - Neural Cloud Platform for Brain-Computer Interfaces

<div align="center">

[![CodeQL](https://github.com/identity-wael/neurascale/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/identity-wael/neurascale/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/identity-wael/neurascale/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/identity-wael/neurascale/actions/workflows/dependency-review.yml)
[![Neon Database](https://img.shields.io/badge/Database-Neon-00E599)](https://neon.tech)
[![Sanity CMS](https://img.shields.io/badge/CMS-Sanity-F03E2F)](https://sanity.io)
[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000)](https://vercel.com)
[![pnpm](https://img.shields.io/badge/Maintained%20with-pnpm-f9ad00)](https://pnpm.io)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

## 🧠 Overview

NeuraScale is a specialized cloud platform purpose-built for processing petabytes of neural data, enabling next-generation brain-computer interface (BCI) applications. Our infrastructure powers three groundbreaking domains:

- **🦾 NeuroProsthetics**: Restoring mobility with mind-controlled robotic limbs
- **🤖 Brain-Swarm Interface**: Commanding autonomous robot swarms with neural intent
- **🥽 Full-Dive VR**: Achieving true immersion in virtual realities

Built on AWS and NVIDIA's cutting-edge platforms, NeuraScale provides the computational backbone for real-time neural signal processing, advanced machine learning, and seamless brain-machine integration.

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18.x or higher
- **pnpm** 9.x or higher ([install guide](https://pnpm.io/installation))
- **Git** for version control
- **Vercel CLI** (optional) for deployment

### Installation

```bash
# Clone the repository
git clone https://github.com/identity-wael/neurascale.git
cd neurascale

# Install dependencies using pnpm
pnpm install

# Navigate to the web app
cd apps/web

# Copy environment variables
cp .env.example .env.local

# Start development server
pnpm dev
```

Visit `http://localhost:3000` to see the application running.

## 📁 Project Architecture

### Repository Structure

```
neurascale/
├── apps/                         # Application workspace
│   ├── web/                      # Main web application (Next.js 15)
│   │   ├── app/                 # App Router pages & API routes
│   │   ├── components/          # React components
│   │   │   ├── layout/         # Layout components (Header, Footer)
│   │   │   ├── sections/       # Page sections
│   │   │   ├── ui/            # Reusable UI components
│   │   │   └── visuals/        # 3D visualizations (Three.js)
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utilities and configurations
│   │   ├── public/             # Static assets
│   │   ├── scripts/            # Build and migration scripts
│   │   ├── src/                # Additional source code
│   │   │   ├── contexts/       # React contexts
│   │   │   ├── lib/           # Core libraries
│   │   │   ├── sanity/        # Sanity CMS schemas
│   │   │   └── types/         # TypeScript definitions
│   │   └── package.json        # App dependencies
│   └── packages/                # Shared packages workspace
│       ├── eslint-config/      # Shared ESLint configuration
│       ├── typescript-config/  # Shared TypeScript config
│       └── test-utils/         # Testing utilities
├── console/                     # NeuraScale Console application
│   ├── app/                    # Console app pages
│   ├── infrastructure/         # Terraform & GCP configs
│   └── docs/                   # Console documentation
├── docs/                        # Project documentation
├── docs-site/                   # GitHub Pages documentation
├── .github/                     # GitHub configurations
│   ├── workflows/              # CI/CD pipelines
│   └── scripts/                # Automation scripts
├── .pnpmfile.cjs               # pnpm configuration
├── package.json                # Root package.json
├── pnpm-workspace.yaml         # pnpm workspace config
└── turbo.json                  # Turborepo configuration
```

## 🛠️ Technology Stack

### Core Technologies

| Category            | Technology                                    | Purpose                            |
| ------------------- | --------------------------------------------- | ---------------------------------- |
| **Framework**       | [Next.js 15](https://nextjs.org/)             | React framework with App Router    |
| **Language**        | [TypeScript](https://www.typescriptlang.org/) | Type-safe JavaScript               |
| **Package Manager** | [pnpm](https://pnpm.io/)                      | Fast, efficient package management |
| **Monorepo**        | [Turborepo](https://turbo.build/)             | High-performance build system      |

### Backend & Infrastructure

| Category           | Technology                               | Purpose                            |
| ------------------ | ---------------------------------------- | ---------------------------------- |
| **Database**       | [Neon](https://neon.tech)                | Serverless Postgres with branching |
| **CMS**            | [Sanity](https://sanity.io)              | Headless content management        |
| **Authentication** | [NextAuth.js](https://next-auth.js.org/) | Authentication for Next.js         |
| **Email**          | [Nodemailer](https://nodemailer.com/)    | Email sending service              |
| **Payments**       | [Stripe](https://stripe.com)             | Payment processing (Console app)   |

### Frontend & Design

| Category          | Technology                                                  | Purpose                     |
| ----------------- | ----------------------------------------------------------- | --------------------------- |
| **Styling**       | [Tailwind CSS](https://tailwindcss.com/)                    | Utility-first CSS framework |
| **3D Graphics**   | [Three.js](https://threejs.org/)                            | 3D visualizations           |
| **3D React**      | [React Three Fiber](https://docs.pmnd.rs/react-three-fiber) | React renderer for Three.js |
| **3D Components** | [@react-three/drei](https://github.com/pmndrs/drei)         | Useful helpers for R3F      |
| **Animations**    | [Framer Motion](https://www.framer.com/motion/)             | Production-ready animations |
| **Smooth Scroll** | [Lenis](https://lenis.studiofreight.com/)                   | Smooth scroll library       |

### Cloud & DevOps

| Category      | Technology                                            | Purpose                  |
| ------------- | ----------------------------------------------------- | ------------------------ |
| **Hosting**   | [Vercel](https://vercel.com)                          | Edge deployment platform |
| **Analytics** | [Google Analytics 4](https://analytics.google.com/)   | Web analytics            |
| **Maps**      | [Google Maps API](https://developers.google.com/maps) | Location services        |
| **CI/CD**     | [GitHub Actions](https://github.com/features/actions) | Automated workflows      |
| **Security**  | [CodeQL](https://codeql.github.com/)                  | Code security analysis   |

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

### Available Scripts

```bash
# Development
pnpm dev              # Start development server
pnpm build            # Build for production
pnpm start            # Start production server
pnpm preview          # Preview production build

# Code Quality
pnpm lint             # Run ESLint
pnpm lint:fix         # Fix linting issues
pnpm format           # Format with Prettier
pnpm typecheck        # TypeScript type checking

# Testing
pnpm test             # Run tests
pnpm test:watch       # Run tests in watch mode
pnpm test:coverage    # Generate coverage report

# Database
pnpm db:push          # Push schema to database
pnpm db:studio        # Open Prisma Studio
pnpm db:generate      # Generate Prisma client
```

### Code Style Guide

- **TypeScript**: Strict mode enabled with comprehensive type checking
- **Components**: Functional components with TypeScript interfaces
- **Styling**: Tailwind CSS with consistent design tokens
- **File Naming**: PascalCase for components, camelCase for utilities
- **Imports**: Absolute imports using `@/` prefix

### Pre-commit Hooks

We use Husky and lint-staged for code quality:

- ✅ Prettier formatting
- ✅ ESLint validation
- ✅ TypeScript checking
- ✅ Build verification
- ✅ Security scanning

## 🏗️ Architecture Overview

### Platform Layers

1. **Neural Interaction & Immersion Layer (NIIL)**

   - User-facing interfaces and analytics
   - Neural identity management
   - Mixed reality experiences
   - Cognitive biometric authentication

2. **Emulation Layer**

   - Neural signal simulation and translation
   - Real-time processing pipeline
   - Machine learning model inference
   - Data transformation services

3. **Physical Integration & Control Layer (PICL)**
   - Direct hardware interfaces
   - Robotic limb control systems
   - Sensor array management
   - Device telemetry and monitoring

### Core Components

- **Neural Management System (NMS)**: Central orchestration platform
- **Neural Ledger**: Blockchain-based data integrity system
- **Extended Reality Engine**: VR/XR rendering and interaction
- **Neural Applications**: Domain-specific BCI applications

## 🔐 Security

### Security Features

- **Data Encryption**: End-to-end encryption for neural data
- **Access Control**: Role-based permissions with biometric auth
- **Compliance**: HIPAA and GDPR compliant architecture
- **Audit Logging**: Comprehensive activity tracking
- **Vulnerability Scanning**: Automated security checks with CodeQL

### Reporting Security Issues

Please see our [Security Policy](SECURITY.md) for reporting vulnerabilities.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow the existing code style and conventions
- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

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

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><strong>Build fails with module not found errors</strong></summary>

```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

</details>

<details>
<summary><strong>Environment variables not loading</strong></summary>

- Ensure `.env.local` exists in `apps/web/`
- Check variable names match exactly (case-sensitive)
- Restart the development server after changes
</details>

<details>
<summary><strong>Sanity Studio not accessible</strong></summary>

- Verify Sanity project ID and dataset in `.env.local`
- Check you're logged in: `pnpm sanity login`
- Ensure CORS is configured in Sanity dashboard
</details>

<details>
<summary><strong>Database connection issues</strong></summary>

- Verify `DATABASE_URL` is set correctly
- Check Neon dashboard for service status
- Ensure IP is whitelisted (if applicable)
</details>

### Getting Help

- 📚 Check our [comprehensive documentation](https://docs.neurascale.io)
- 💬 Join our [Discord community](https://discord.gg/neurascale)
- 🐛 Report bugs via [GitHub Issues](https://github.com/identity-wael/neurascale/issues)
- 📧 Contact support: support@neurascale.io

## 📈 Project Status

- ✅ **Phase 1**: Platform infrastructure (Complete)
- ✅ **Phase 2**: Core BCI applications (Complete)
- 🚧 **Phase 3**: ML model integration (In Progress)
- 📅 **Phase 4**: Hardware partnerships (Q2 2025)
- 📅 **Phase 5**: Clinical trials (Q4 2025)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

### Project Links

- 🌐 [Website](https://neurascale.com)
- 📖 [Documentation](https://docs.neurascale.io)
- 🎨 [Sanity Studio](https://neurascale.com/studio)
- 💻 [GitHub Repository](https://github.com/identity-wael/neurascale)
- 🚀 [Live Demo](https://neurascale.vercel.app)

### Community

- 💬 [Discord Server](https://discord.gg/neurascale)
- 🐦 [Twitter/X](https://twitter.com/neurascale)
- 💼 [LinkedIn](https://linkedin.com/company/neurascale)
- 📧 [Newsletter](https://neurascale.com/newsletter)

### Technical Resources

- 📚 [API Documentation](https://docs.neurascale.io/api)
- 🧠 [BCI Research Papers](https://neurascale.com/research)
- 🎓 [Developer Tutorials](https://neurascale.com/tutorials)
- 🔧 [Status Page](https://status.neurascale.io)

---

<div align="center">

**Built with ❤️ and 🧠 by the NeuraScale Team**

_Bridging Mind and World Through Advanced Neural Cloud Technology_

</div>
