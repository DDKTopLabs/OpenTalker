"""
TTS Service - FastAPI Application
Qwen3-TTS Text-to-Speech Service
"""

import asyncio
import logging
import os
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import settings
from app.service import Qwen3TTSService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenTalker TTS Service",
    description="Qwen3-TTS Text-to-Speech Service",
    version="0.3.0",
)

# Initialize TTS service
tts_service = Qwen3TTSService()


class TTSRequest(BaseModel):
    """TTS request model"""

    input: str = Field(..., description="Text to synthesize", min_length=1, max_length=4096)
    speaker: Optional[str] = Field(default=None, description="Speaker name")
    language: Optional[str] = Field(default=None, description="Language code (zh/en/ja/ko/etc)")
    response_format: str = Field(default="wav", description="Audio format")
    speed: float = Field(default=1.0, description="Speech speed", ge=0.25, le=4.0)


@app.on_event("startup")
async def startup_event():
    """Startup event - load model"""
    logger.info("Starting TTS Service")
    logger.info(f"Model: {settings.qwen_tts_model}")
    logger.info(f"Device: {settings.qwen_tts_device}")
    logger.info(f"HF Endpoint: {settings.hf_endpoint}")

    # Set HuggingFace endpoint
    os.environ["HF_ENDPOINT"] = settings.hf_endpoint

    # Load model
    try:
        logger.info("Loading Qwen3-TTS model...")
        tts_service.load_model()
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}", exc_info=True)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if tts_service.is_loaded else "loading",
        "service": "tts",
        "model": settings.qwen_tts_model,
        "device": settings.qwen_tts_device,
        "model_loaded": tts_service.is_loaded,
    }


@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    """
    Synthesize speech from text

    Args:
        request: TTS request with text, speaker, and options

    Returns:
        Audio file in requested format
    """
    try:
        logger.info(
            f"Synthesis request: format={request.response_format}, "
            f"text_length={len(request.input)}, speed={request.speed}"
        )

        # Perform synthesis
        start_time = time.time()

        audio_bytes = await asyncio.to_thread(
            tts_service.synthesize,
            text=request.input,
            speaker=request.speaker,
            language=request.language,
            response_format=request.response_format,
            speed=request.speed,
        )

        elapsed = time.time() - start_time
        logger.info(f"Synthesis completed in {elapsed:.2f}s, output size: {len(audio_bytes)} bytes")

        # Determine media type
        media_types = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "flac": "audio/flac",
            "opus": "audio/opus",
        }
        media_type = media_types.get(request.response_format, "audio/wav")

        # Return audio response
        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="speech.{request.response_format}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower(),
    )
