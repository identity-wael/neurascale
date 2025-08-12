# Multi-stage Dockerfile for Neural Engine CLI Tool
# Interactive command-line interface for neural data processing

# Stage 1: Dependencies
FROM python:3.12.11-slim-bookworm AS dependencies
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
# Use minimal requirements for faster CI builds
COPY neural-engine/requirements-minimal.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        click==8.1.7 \
        rich==13.7.0 \
        prompt-toolkit==3.0.43 \
        tabulate==0.9.0

# Stage 2: Builder
FROM python:3.12.11-slim-bookworm AS builder
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY neural-engine/src/cli ./cli
COPY neural-engine/src/utils ./utils
COPY neural-engine/src/api ./api
COPY neural-engine/src/processors ./processors
COPY neural-engine/src/devices ./devices
COPY neural-engine/processing ./processing
COPY neural-engine/models ./models

# Compile Python files
RUN python -m compileall -b .

# Create CLI entry point script
RUN echo '#!/bin/bash\npython -m cli.main "$@"' > /app/neural-cli && \
    chmod +x /app/neural-cli

# Stage 3: Runtime
FROM python:3.12.11-slim-bookworm AS runtime
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libhdf5-103 \
    ca-certificates \
    curl \
    vim \
    less \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with home directory
RUN groupadd -r neural && useradd -r -g neural -m neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy application
COPY --from=builder --chown=neural:neural /app /app

# Set environment variables
ENV PATH="/opt/venv/bin:/app:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NEURAL_CLI_HOME=/home/neural/.neural-cli

# Create CLI config directory
RUN mkdir -p /home/neural/.neural-cli && \
    chown -R neural:neural /home/neural/.neural-cli

WORKDIR /workspace

# Switch to non-root user
USER neural

# Create workspace directory
RUN mkdir -p /workspace

# Set up shell configuration
RUN echo 'alias ncli="neural-cli"' >> ~/.bashrc && \
    echo 'alias nec="neural-cli connect"' >> ~/.bashrc && \
    echo 'alias nes="neural-cli stream"' >> ~/.bashrc && \
    echo 'alias nep="neural-cli process"' >> ~/.bashrc && \
    echo 'export PS1="\[\033[36m\]neural-cli\[\033[m\]:\[\033[33m\]\w\[\033[m\]$ "' >> ~/.bashrc

# Default command - interactive shell
CMD ["/bin/bash"]

# Alternative entry point for direct CLI usage
ENTRYPOINT ["neural-cli"]
