"""
Gateway - FastAPI Application
OpenAI-compatible Audio API Gateway
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import audio, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenTalker API Gateway",
    description="OpenAI-compatible Audio API - STT & TTS Services",
    version="0.3.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(audio.router, prefix="/v1/audio", tags=["Audio"])


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("Starting OpenTalker API Gateway")
    logger.info(f"STT Service: {settings.stt_service_url}")
    logger.info(f"TTS Service: {settings.tts_service_url}")
    logger.info("Gateway ready!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.gateway_host,
        port=settings.gateway_port,
        log_level=settings.log_level.lower(),
    )
