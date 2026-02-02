# ============================================
# OpenTalker - Dockerfile
# Base: NVIDIA CUDA 12.3.2 with cuDNN 9
# Optimized for GTX 1050 Ti (4GB VRAM)
# ============================================

FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# ============================================
# Replace Ubuntu APT sources with Tsinghua mirror
# ============================================
RUN sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list

# ============================================
# Install system dependencies
# ============================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python 3.11
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    # Audio processing
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    # Build tools
    build-essential \
    pkg-config \
    # Utilities
    curl \
    wget \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# ============================================
# Install uv package manager
# ============================================
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# ============================================
# Set working directory
# ============================================
WORKDIR /app

# ============================================
# Copy dependency files
# ============================================
COPY pyproject.toml .
COPY .python-version .

# ============================================
# Install Python dependencies using uv
# Mirror sources are configured in pyproject.toml
# ============================================
RUN uv pip install --system --no-cache -e .

# ============================================
# Copy application code
# ============================================
COPY app/ ./app/
COPY scripts/ ./scripts/

# ============================================
# Create necessary directories
# ============================================
RUN mkdir -p /models/qwen3-asr \
    /models/indextts \
    /models/.cache/huggingface \
    /app/tmp \
    && chmod -R 777 /models /app/tmp

# ============================================
# Expose port
# ============================================
EXPOSE 8000

# ============================================
# Health check
# ============================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ============================================
# Set entrypoint
# ============================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
