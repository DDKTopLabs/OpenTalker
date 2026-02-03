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
ENV PATH="/root/.local/bin:${PATH}"

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
# Strategy: Install PyTorch first, then install dependencies from pyproject.toml
# but override the index URLs to use official sources for CI reliability
# ============================================
RUN /root/.local/bin/uv pip install --system --no-cache \
    torch>=2.1.0 torchaudio>=2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121 && \
    /root/.local/bin/uv pip install --system --no-cache \
    fastapi>=0.109.0 \
    uvicorn[standard]>=0.27.0 \
    python-multipart>=0.0.6 \
    pydantic>=2.5.0 \
    pydantic-settings>=2.1.0 \
    transformers>=4.40.0 \
    qwen-asr>=0.0.6 \
    sentencepiece>=0.1.99 \
    librosa>=0.10.0 \
    soundfile>=0.12.0 \
    scipy>=1.10.0 \
    "numpy>=1.24.0,<2.0.0" \
    ffmpeg-python>=0.2.0 \
    tqdm>=4.65.0 \
    python-dotenv>=1.0.0 \
    requests>=2.31.0 \
    --index-url https://pypi.org/simple

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
