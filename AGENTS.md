# AGENTS.md - Developer Guide for AI Coding Agents

This document provides essential information for AI coding agents working in this repository.

## Project Overview

**OpenTalker** - OpenAI-compatible audio processing API server supporting Speech-to-Text (STT) and Text-to-Speech (TTS), optimized for GTX 1050 Ti (4GB VRAM).

- **Framework**: FastAPI
- **Language**: Python 3.10-3.12
- **Package Manager**: uv (fast Python package manager)
- **Models**: Qwen3-ASR (STT), IndexTTS2 (TTS)
- **Deployment**: Docker with GPU support

## ⚠️ Critical Rules

**NEVER use `python` or `pip` commands directly. ALWAYS use `uv` commands instead.**

This project uses `uv` as the package manager for faster dependency resolution and better reproducibility.

```bash
# ❌ WRONG - Do NOT use these
python script.py
pip install package
python -m pytest

# ✅ CORRECT - Use these instead
uv run python script.py
uv pip install package
uv run pytest
```

## Build, Lint, and Test Commands

### Environment Setup

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]" --index-strategy unsafe-best-match

# Install system dependencies (Ubuntu)
sudo apt-get install -y ffmpeg libsndfile1 libsndfile1-dev
```

### Linting and Formatting

```bash
# Run ruff linter (checks code quality)
uv run ruff check app/ tests/

# Auto-fix ruff issues
uv run ruff check app/ tests/ --fix

# Check code formatting with black
uv run black --check app/ tests/

# Auto-format code with black
uv run black app/ tests/

# Run type checking with mypy
uv run mypy app/ --ignore-missing-imports
```

### Testing

```bash
# Run all tests (excluding GPU tests)
uv run pytest tests/ -v -m "not gpu" --cov=app --cov-report=term-missing

# Run a single test file
uv run pytest tests/test_sample.py -v

# Run a single test class
uv run pytest tests/test_sample.py::TestHealthEndpoint -v

# Run a single test function
uv run pytest tests/test_sample.py::TestHealthEndpoint::test_health_check_structure -v

# Run with coverage report
uv run pytest tests/ -v --cov=app --cov-report=html

# Run GPU tests (requires CUDA)
uv run pytest tests/ -v -m gpu

# Run slow tests
uv run pytest tests/ -v -m slow
```

### Running the Application

```bash
# Development mode (with auto-reload)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

# Run Python scripts
uv run python scripts/init_models.py

# Using Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

## Code Style Guidelines

### General Principles

- **Line Length**: Maximum 100 characters
- **Python Version**: Target 3.10+ features
- **Formatting**: Use Black (enforced in CI)
- **Linting**: Use Ruff (enforced in CI)
- **Type Checking**: Use MyPy (optional but recommended)

### Import Organization

Follow this order (enforced by Ruff):

```python
# 1. Standard library imports
import asyncio
import logging
import os
from typing import Optional

# 2. Third-party imports
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# 3. Local application imports
from app.config import settings
from app.models import TTSRequest
```

### Naming Conventions

- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`
- **Modules**: `lowercase_with_underscores.py`

```python
# Good examples
class ModelManager:
    def __init__(self):
        self._current_model = None
        
    async def switch_to_stt(self):
        pass

MAX_UPLOAD_SIZE = 52428800
settings = Settings()
```

### Type Hints

Always use type hints for function parameters and return values:

```python
# Good
async def transcribe(
    audio_path: str,
    language: Optional[str] = None,
    temperature: float = 0.0
) -> dict:
    pass

# Avoid
async def transcribe(audio_path, language=None, temperature=0.0):
    pass
```

### Docstrings

Use triple-quoted docstrings for modules, classes, and functions:

```python
"""
Module-level docstring explaining the purpose of this file
"""

class AudioProcessor:
    """
    Class docstring explaining what this class does
    """
    
    def process_audio(self, audio_path: str) -> bytes:
        """
        Function docstring explaining what this function does
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Processed audio as bytes
        """
        pass
```

### Error Handling

Use FastAPI's HTTPException with OpenAI-compatible error responses:

```python
from fastapi import HTTPException, status
from app.utils import openai_compat

# Validation errors
validation_error = openai_compat.validate_transcription_request(...)
if validation_error:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=validation_error.model_dump(),
    )

# Service unavailable
error = openai_compat.create_model_not_ready_error("stt")
raise HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail=error.model_dump(),
)

# Internal errors
try:
    result = await process_audio()
except Exception as e:
    logger.error(f"Processing failed: {e}", exc_info=True)
    error = openai_compat.create_processing_error("audio processing", str(e))
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error.model_dump(),
    )
```

### Logging

Use Python's logging module with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debugging information")
logger.info("General informational messages")
logger.warning("Warning messages for potential issues")
logger.error("Error messages", exc_info=True)  # Include traceback
logger.critical("Critical errors that may cause shutdown")
```

### Configuration Management

Use Pydantic Settings for configuration:

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
```

### Async/Await Patterns

Use async/await for I/O operations:

```python
# For CPU-bound operations, use asyncio.to_thread
result = await asyncio.to_thread(
    cpu_intensive_function,
    arg1,
    arg2
)

# For async operations
async def process_request():
    await model_manager.switch_to_stt()
    result = await stt_service.transcribe(audio_path)
    return result
```

## Testing Guidelines

### Test Structure

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Name test classes as `Test*`
- Name test functions as `test_*`

### Test Markers

Use pytest markers to categorize tests:

```python
import pytest

# GPU-dependent tests (skipped in CI)
@pytest.mark.gpu
def test_model_loading():
    pass

# Slow tests
@pytest.mark.slow
def test_large_file_processing():
    pass
```

### Test Organization

```python
class TestHealthEndpoint:
    """Test health check endpoint (no GPU required)."""
    
    def test_health_check_structure(self):
        """Test that health check returns expected structure."""
        assert True
```

## Project Structure

```
.
├── app/                    # Main application code
│   ├── core/              # Core functionality (model manager, GPU monitor)
│   ├── routers/           # FastAPI route handlers
│   ├── services/          # Business logic (STT, TTS services)
│   ├── utils/             # Utility functions
│   ├── config.py          # Configuration management
│   ├── models.py          # Pydantic models
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test files
├── scripts/               # Utility scripts
├── models/                # Model cache directory
├── pyproject.toml         # Project configuration
├── docker-compose.yml     # Docker deployment
└── Dockerfile             # Docker image definition
```

## Common Patterns

### FastAPI Router Pattern

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/endpoint")
async def endpoint_handler(request: RequestModel):
    """Endpoint docstring"""
    try:
        # Process request
        result = await process_request(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Model Manager Pattern

```python
# Switch models before use
await model_manager.switch_to_stt()
stt_service = model_manager.get_stt_service()

await model_manager.switch_to_tts()
tts_service = model_manager.get_tts_service()
```

## Important Notes

1. **GPU Memory**: This project is optimized for 4GB VRAM. STT and TTS models cannot be loaded simultaneously.
2. **Model Switching**: Expect 5-10 seconds for model switching operations.
3. **Async Operations**: Use `asyncio.to_thread()` for CPU-bound operations to avoid blocking.
4. **Temp Files**: Always clean up temporary files in `finally` blocks.
5. **Mirror Sources**: Project uses Tsinghua University mirrors for faster downloads in China.
6. **Environment Variables**: All configuration is via environment variables (see `.env.example`).

## CI/CD

The project uses GitHub Actions for CI:

- **Lint Job**: Runs ruff, black, and mypy
- **Test Job**: Runs pytest with CPU-only PyTorch
- **Docker Build**: Validates Docker image builds
- **Security**: Runs Trivy vulnerability scanner

All checks must pass before merging PRs.
