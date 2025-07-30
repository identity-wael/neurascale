# Base ML image for Neural Engine services
# Provides comprehensive ML/AI libraries with GPU support

FROM nvidia/cuda:12.2.0-devel-ubuntu22.04 AS ml-base

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.12

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    software-properties-common \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    # Build tools
    build-essential \
    cmake \
    pkg-config \
    # Scientific computing
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    libnetcdf-dev \
    # Image processing
    libopencv-dev \
    libjpeg-dev \
    libpng-dev \
    # Audio processing
    libsndfile1-dev \
    libportaudio2 \
    # CUDA libraries
    cuda-toolkit-12-2 \
    libcudnn8 \
    libnccl2 \
    # Utilities
    wget \
    curl \
    git \
    vim \
    htop \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install base packages
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel \
    cython

# Install scientific computing stack
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    scipy==1.13.0 \
    pandas==2.2.2 \
    matplotlib==3.8.4 \
    seaborn==0.13.2 \
    scikit-learn==1.4.2 \
    statsmodels==0.14.1

# Install deep learning frameworks
RUN pip install --no-cache-dir \
    torch==2.1.0+cu121 \
    torchvision==0.16.0+cu121 \
    torchaudio==2.1.0+cu121 \
    -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install --no-cache-dir \
    tensorflow[and-cuda]==2.15.0 \
    keras==2.15.0 \
    tensorboard==2.15.0

# Install ML tools
RUN pip install --no-cache-dir \
    transformers==4.36.0 \
    datasets==2.16.0 \
    tokenizers==0.15.0 \
    accelerate==0.25.0 \
    bitsandbytes==0.41.0

# Install signal processing libraries
RUN pip install --no-cache-dir \
    mne==1.6.0 \
    pywavelets==1.5.0 \
    librosa==0.10.1 \
    soundfile==0.12.1

# Install additional ML libraries
RUN pip install --no-cache-dir \
    xgboost==2.0.3 \
    lightgbm==4.2.0 \
    optuna==3.5.0 \
    mlflow==2.9.2 \
    wandb==0.16.2

# Install notebook and visualization tools
RUN pip install --no-cache-dir \
    jupyter==1.0.0 \
    jupyterlab==4.0.10 \
    plotly==5.18.0 \
    dash==2.14.2

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Configure Jupyter
RUN mkdir -p /home/neural/.jupyter && \
    echo "c.NotebookApp.token = ''" > /home/neural/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> /home/neural/.jupyter/jupyter_notebook_config.py && \
    chown -R neural:neural /home/neural/.jupyter

# Set up CUDA environment
ENV CUDA_HOME=/usr/local/cuda \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH \
    CUDA_VISIBLE_DEVICES=0 \
    TF_CPP_MIN_LOG_LEVEL=2

# Create working directory
WORKDIR /workspace
RUN chown neural:neural /workspace

# Switch to non-root user
USER neural

# Verify installations
RUN python -c "import torch; print(f'PyTorch: {torch.__version__}')" && \
    python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')" && \
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Default command
CMD ["python"]
