# Multi-stage Dockerfile for Device Manager Service
# Go-based service for managing BCI device connections

# Stage 1: Builder
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git gcc musl-dev linux-headers

WORKDIR /build

# Copy go mod files
COPY neural-engine/device-manager/go.mod neural-engine/device-manager/go.sum ./
RUN go mod download

# Copy source code
COPY neural-engine/device-manager/ .

# Build the binary
RUN CGO_ENABLED=1 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s" -o device-manager ./cmd/server

# Stage 2: Runtime
FROM alpine:3.19

# Install runtime dependencies
RUN apk add --no-cache ca-certificates libusb-dev bluez-libs

# Create non-root user
RUN addgroup -g 1000 neural && \
    adduser -D -u 1000 -G neural neural

# Copy binary from builder
COPY --from=builder /build/device-manager /usr/local/bin/device-manager

# Create necessary directories
RUN mkdir -p /etc/device-manager /var/log/device-manager && \
    chown -R neural:neural /etc/device-manager /var/log/device-manager

# Copy configuration
COPY neural-engine/device-manager/configs/production.yaml /etc/device-manager/config.yaml

WORKDIR /app

# Switch to non-root user
USER neural

# Expose ports
EXPOSE 8081 50052 9091

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8081/health || exit 1

# Run the service
CMD ["device-manager", "--config", "/etc/device-manager/config.yaml"]
