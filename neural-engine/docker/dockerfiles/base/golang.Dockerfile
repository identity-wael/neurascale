# Base Go image for Neural Engine services
# Provides common Go runtime with necessary tools

FROM golang:1.21-alpine AS golang-base

# Install common build dependencies
RUN apk add --no-cache \
    git \
    gcc \
    musl-dev \
    linux-headers \
    ca-certificates \
    tzdata \
    make \
    bash

# Install common Go tools
RUN go install github.com/go-delve/delve/cmd/dlv@latest && \
    go install github.com/cosmtrek/air@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Create non-root user
RUN addgroup -g 1000 neural && \
    adduser -D -u 1000 -G neural neural

# Set up Go environment
ENV GO111MODULE=on \
    CGO_ENABLED=1 \
    GOOS=linux \
    GOARCH=amd64

# Create standard directories
RUN mkdir -p /app /go/pkg /go/bin && \
    chown -R neural:neural /app /go

WORKDIR /app

# Switch to non-root user
USER neural

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD go version || exit 1
