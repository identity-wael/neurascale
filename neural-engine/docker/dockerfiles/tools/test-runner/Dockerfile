# Test runner container for integration tests
FROM python:3.12.11-slim-bookworm
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/*

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

# Create non-root user
RUN useradd -m -u 1000 testuser
USER testuser

# Default command
CMD ["pytest", "-v", "--tb=short"]
