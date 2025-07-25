# Multi-stage Dockerfile for Neural Engine

# Stage 1: Base image with system dependencies
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    libhdf5-dev \
    libatlas-base-dev \
    gfortran \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as app

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 neural && chown -R neural:neural /app
USER neural

# Default command (can be overridden)
CMD ["python", "-m", "neural_engine"]

# Stage 4: Cloud Functions (for individual function deployment)
FROM dependencies as cloud-function

# Copy only functions code
COPY functions/ /app/functions/
COPY models/ /app/models/
COPY dataflow/ /app/dataflow/

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Cloud Functions expects main.py at root
WORKDIR /app/functions

# Stage 5: API Server
FROM app as api-server

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 6: Inference Server
FROM app as inference-server

# Expose port
EXPOSE 8080

# Run inference server
CMD ["python", "-m", "models.inference_server"]

# Stage 7: Dataflow Worker
FROM dependencies as dataflow-worker

# Copy dataflow code
COPY dataflow/ /app/dataflow/
COPY setup.py /app/

# Install Apache Beam separately for better caching
RUN pip install --no-cache-dir apache-beam[gcp]

# Set working directory
WORKDIR /app/dataflow

# Default to DirectRunner for testing
ENV RUNNER=DirectRunner

CMD ["python", "neural_processing_pipeline.py"]
