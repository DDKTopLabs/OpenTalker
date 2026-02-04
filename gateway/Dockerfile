# ============================================
# OpenTalker Gateway - Dockerfile
# Lightweight API Gateway (no GPU required)
# ============================================

FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install Python dependencies
RUN /root/.local/bin/uv pip install --system --no-cache \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    python-multipart>=0.0.12 \
    pydantic>=2.9.0 \
    pydantic-settings>=2.6.0 \
    httpx>=0.27.0 \
    --index-url https://pypi.org/simple

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
