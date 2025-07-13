# Deployment Configuration

## Vercel Setup

Since the Next.js application has been moved to the `webapp/` subdirectory, you need to update your Vercel project configuration:

### Update Vercel Project Settings

1. Go to your Vercel dashboard
2. Select your Neurascale project
3. Navigate to **Settings** → **General**
4. Find the **Root Directory** setting
5. Change it from `.` (root) to `webapp`
6. Save the changes

### Alternative: Use vercel.json

Alternatively, you can create a `vercel.json` file in the root directory with the following configuration:

```json
{
  "buildCommand": "cd webapp && npm run build",
  "outputDirectory": "webapp/.next",
  "installCommand": "cd webapp && npm install",
  "rootDirectory": "webapp"
}
```

## Project Structure After Reorganization

```
/
├── webapp/              # Next.js web application
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   ├── public/         # Static assets
│   ├── package.json    # Web app dependencies
│   ├── next.config.mjs # Next.js configuration
│   └── ...             # Other Next.js config files
├── README.md           # Project documentation
├── AGENTS.md          # Development guidelines
├── DEPLOYMENT.md      # This file
└── .gitignore         # Git ignore rules
```

## Benefits of This Structure

1. **Clean Separation**: Web application is clearly separated from other potential components
2. **Scalable**: Easy to add infrastructure, APIs, or other services
3. **Maintainable**: Each component has its own dependencies and configuration
4. **CI/CD Ready**: Each folder can have its own deployment pipeline

## Development Workflow

All development commands should now be run from the `webapp/` directory:

```bash
cd webapp
npm install
npm run dev
npm run build
npm run lint
```