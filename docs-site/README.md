# NeuraScale Documentation Site

This directory contains the Jekyll-based documentation site for NeuraScale, designed to be hosted on GitHub Pages.

## Local Development

### Prerequisites

- Ruby 2.7 or higher
- Bundler gem (`gem install bundler`)

### Setup

1. Install dependencies:

   ```bash
   cd docs-site
   bundle install
   ```

2. Run the local server:

   ```bash
   bundle exec jekyll serve
   ```

3. Open http://localhost:4000/neurascale in your browser

### Building for Production

```bash
bundle exec jekyll build
```

The built site will be in the `_site` directory.

## Directory Structure

```
docs-site/
├── _config.yml              # Jekyll configuration
├── _docs/                   # Documentation collection
├── _console/                # Console documentation collection
├── _layouts/                # Page layouts
├── _includes/               # Reusable components
├── assets/                  # CSS, JS, images
│   └── css/
│       └── style.scss       # Custom styles
├── index.md                 # Homepage
├── architecture.md          # Technical architecture
├── architecture-diagrams.md # Visual architecture diagrams
├── api-documentation.md     # API reference
├── neural-management-system.md
├── dataset-management.md
├── security-encryption.md
├── contributing.md          # Contributing guide
├── security.md              # Security policy
└── Gemfile                  # Ruby dependencies
```

## Key Documentation Pages

### Architecture Documentation

- `/architecture/` - Technical architecture overview with system design principles
- `/architecture-diagrams/` - Comprehensive visual diagrams including:
  - System Architecture Overview
  - Device Data Flow
  - Real-Time Processing Pipeline
  - Multi-Device Synchronization
  - Security Architecture
  - Deployment Architecture
  - Database Architecture
  - API Gateway Architecture
  - Performance Monitoring Dashboard

### API Documentation

- `/api-documentation/` - Complete REST and WebSocket API reference with examples

## Deployment

The site is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment is handled by the GitHub Actions workflow in `.github/workflows/deploy-docs.yml`.

### Manual Deployment

If needed, you can manually deploy:

1. Build the site:

   ```bash
   bundle exec jekyll build --baseurl /neurascale
   ```

2. The site will be available at: https://[username].github.io/neurascale/

## Adding New Documentation

### To add a new documentation page:

1. Create a new `.md` file in the appropriate collection directory (`_docs/` or `_console/`)

2. Add front matter:

   ```yaml
   ---
   layout: doc
   title: Your Page Title
   description: Brief description
   ---
   ```

3. Write your content in Markdown

4. Update `_config.yml` navigation if needed

## Theme Customization

The site uses Jekyll's minimal theme as a base. Custom styles are in `assets/css/style.scss`.

To change themes:

1. Update the `theme` in `_config.yml`
2. Adjust layouts and styles as needed

## Troubleshooting

### Build Errors

- Ensure all dependencies are installed: `bundle install`
- Check Jekyll version compatibility
- Verify front matter syntax in markdown files

### Deployment Issues

- Check GitHub Pages settings in repository
- Verify the GitHub Actions workflow has proper permissions
- Ensure the base URL matches your repository name
