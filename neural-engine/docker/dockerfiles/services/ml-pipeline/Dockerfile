# Multi-stage Dockerfile for ML Pipeline Service
# Python-based machine learning inference service with GPU support

# Stage 1: Dependencies
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS dependencies

# Prevent interactive prompts
ARG DEBIAN_FRONTEND=noninteractive

# Install Python and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    build-essential \
    cuda-toolkit-12-2 \
    libcudnn8 \
    libnccl2 \
    libhdf5-dev \
    libopenblas-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install requirements
COPY neural-engine/ml-pipeline/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ML frameworks
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    tensorflow==2.15.0 \
    onnxruntime-gpu==1.16.0 \
    transformers==4.36.0

# Stage 2: Builder
FROM dependencies AS builder

WORKDIR /app

# Copy source code
COPY neural-engine/ml-pipeline/ .

# Compile Python files
RUN python -m compileall -b .

# Stage 3: Runtime
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    libgomp1 \
    libhdf5-103 \
    libopenblas0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy application
COPY --from=builder --chown=neural:neural /app /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CUDA_VISIBLE_DEVICES=0 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Create model cache directory
RUN mkdir -p /app/models /app/cache && \
    chown -R neural:neural /app

WORKDIR /app

# Switch to non-root user
USER neural

# Model volume for persistence
VOLUME ["/app/models"]

# Expose ports
EXPOSE 8082 50053 9093

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8082/health').raise_for_status()"

# Run the service
CMD ["python", "-m", "src.server", "--host", "0.0.0.0", "--port", "8082"]
