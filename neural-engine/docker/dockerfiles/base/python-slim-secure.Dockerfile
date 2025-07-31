# Secure Python base using slim with security updates
# Alternative to Alpine for packages that require glibc (TensorFlow, PyTorch)

FROM python:3.12-slim-bookworm AS python-base

# Security updates and minimal packages only
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Set security options
RUN echo "Defaults requiretty" >> /etc/sudoers && \
    echo "neural ALL=(ALL) NOPASSWD: /bin/false" >> /etc/sudoers

# Harden the container
RUN chmod 700 /root && \
    chmod 750 /home/neural

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
USER neural
