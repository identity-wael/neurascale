# Test runner container for integration tests
FROM python:3.13-alpine

# Install dependencies for Alpine
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    curl \
    bash \
    netcat-openbsd

# Install Python test dependencies
RUN pip install --no-cache-dir \
    pytest==7.4.4 \
    pytest-asyncio==0.23.3 \
    pytest-timeout==2.2.0 \
    pytest-xdist==3.5.0 \
    requests==2.31.0 \
    httpx==0.26.0 \
    websocket-client==1.7.0

WORKDIR /tests

# Create non-root user (Alpine uses adduser, not useradd)
RUN adduser -D -u 1000 testuser
USER testuser

# Default command
CMD ["pytest", "-v", "--tb=short"]
