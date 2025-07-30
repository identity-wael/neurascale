# Multi-stage Dockerfile for API Gateway Service
# Node.js-based GraphQL/REST API gateway

# Stage 1: Dependencies
FROM node:20-alpine AS dependencies

WORKDIR /app

# Copy package files
COPY neural-engine/api-gateway/package*.json ./

# Install production dependencies
RUN npm ci --only=production

# Copy dependencies for builder stage
RUN cp -R node_modules prod_node_modules

# Install all dependencies (including dev)
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copy source code
COPY neural-engine/api-gateway/ .

# Build TypeScript
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runtime

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1000 neural && \
    adduser -D -u 1000 -G neural neural

WORKDIR /app

# Copy production dependencies
COPY --from=dependencies /app/prod_node_modules ./node_modules

# Copy built application
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# Copy GraphQL schema files
COPY neural-engine/api-gateway/src/schema ./schema

# Create necessary directories
RUN mkdir -p logs && chown -R neural:neural /app

# Switch to non-root user
USER neural

# Expose ports
EXPOSE 4000 9092

# Environment variables
ENV NODE_ENV=production \
    PORT=4000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:4000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); })"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the server
CMD ["node", "dist/server.js"]
