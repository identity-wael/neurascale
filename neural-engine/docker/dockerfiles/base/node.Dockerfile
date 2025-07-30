# Base Node.js image for Neural Engine services
# Provides common Node.js runtime with TypeScript support

FROM node:20-alpine AS node-base

# Install common dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    ca-certificates \
    dumb-init

# Install global npm packages
RUN npm install -g \
    typescript@5.3.3 \
    ts-node@10.9.2 \
    nodemon@3.0.2 \
    pm2@5.3.0 \
    pino-pretty@10.3.0

# Create non-root user
RUN addgroup -g 1000 neural && \
    adduser -D -u 1000 -G neural neural

# Set npm configuration
RUN npm config set update-notifier false && \
    npm config set fund false

# Create app directory
RUN mkdir -p /app && chown -R neural:neural /app

WORKDIR /app

# Switch to non-root user
USER neural

# Environment variables
ENV NODE_ENV=production \
    NPM_CONFIG_LOGLEVEL=warn \
    NODE_OPTIONS="--enable-source-maps"

# Use dumb-init to handle signals
ENTRYPOINT ["dumb-init", "--"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "process.exit(0)" || exit 1
