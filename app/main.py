"""
FastAPI application initialization and configuration
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import audio, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting OpenAI-compatible Audio API Server")

    logger.info(f"Python version: {sys.version}")
    logger.info(f"CUDA visible devices: {settings.cuda_visible_devices}")
    logger.info(f"HuggingFace endpoint: {settings.hf_endpoint}")
    logger.info(f"Model cache directory: {settings.huggingface_hub_cache}")

    # Set HuggingFace mirror
    os.environ["HF_ENDPOINT"] = settings.hf_endpoint
    os.environ["HUGGINGFACE_HUB_CACHE"] = settings.huggingface_hub_cache

    # Initialize model manager
    from app.core.model_manager import model_manager

    await model_manager.initialize()

    logger.info("Server startup complete")

    yield

    # Shutdown
    logger.info("Shutting down server")
    # Cleanup model manager
    await model_manager.cleanup()
    logger.info("Server shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="OpenAI-compatible Audio API",
    description="Speech-to-Text (Qwen3-ASR) and Text-to-Speech (IndexTTS2) API server",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(audio.router, prefix="/v1/audio", tags=["audio"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpenAI-compatible Audio API Server",
        "version": "0.1.0",
        "endpoints": {
            "transcriptions": "/v1/audio/transcriptions",
            "speech": "/v1/audio/speech",
            "health": "/health",
            "models": "/v1/models",
        },
    }
