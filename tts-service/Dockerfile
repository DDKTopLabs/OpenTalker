# ============================================
# OpenTalker TTS Service - Dockerfile
# Qwen3-TTS Text-to-Speech with GPU support
# ============================================

FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install PyTorch with CUDA support first
RUN /root/.local/bin/uv pip install --system --no-cache \
    torch>=2.1.0 torchaudio>=2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
RUN /root/.local/bin/uv pip install --system --no-cache \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    python-multipart>=0.0.12 \
    pydantic>=2.9.0 \
    pydantic-settings>=2.6.0 \
    qwen-tts>=0.0.5 \
    soundfile>=0.12.0 \
    "numpy>=1.24.0,<2.0.0" \
    --index-url https://pypi.org/simple

# Copy application code
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p /app/tmp /models && chmod -R 777 /app/tmp /models

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
