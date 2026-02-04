"""
STT Service - FastAPI Application
Qwen3-ASR Speech-to-Text Service
"""

import asyncio
import logging
import os
import tempfile
import time
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.config import settings
from app.service import QwenASRService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenTalker STT Service",
    description="Qwen3-ASR Speech-to-Text Service",
    version="0.2.0",
)

# Initialize STT service
stt_service = QwenASRService()


@app.on_event("startup")
async def startup_event():
    """Startup event - load model"""
    logger.info("Starting STT Service")
    logger.info(f"Model: {settings.qwen_asr_model}")
    logger.info(f"Device: {settings.qwen_asr_device}")
    logger.info(f"HF Endpoint: {settings.hf_endpoint}")

    # Set HuggingFace endpoint
    os.environ["HF_ENDPOINT"] = settings.hf_endpoint

    # Load model
    try:
        logger.info("Loading Qwen3-ASR model...")
        stt_service.load_model()
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}", exc_info=True)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if stt_service.is_loaded else "loading",
        "service": "stt",
        "model": settings.qwen_asr_model,
        "device": settings.qwen_asr_device,
        "model_loaded": stt_service.is_loaded,
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(default=None, description="Language code"),
    response_format: str = Form(default="json", description="Response format"),
    timestamp_granularities: Optional[str] = Form(
        default=None, description="Comma-separated: word,segment"
    ),
    temperature: Optional[float] = Form(default=0.0, description="Sampling temperature"),
):
    """
    Transcribe audio to text

    Args:
        file: Audio file (MP3, WAV, FLAC, M4A, OGG, WEBM)
        language: Language code (e.g., 'Chinese', 'English')
        response_format: Output format (json, text, srt, vtt, verbose_json)
        timestamp_granularities: Timestamp types (word, segment)
        temperature: Sampling temperature (0.0-1.0)

    Returns:
        Transcription result in requested format
    """
    try:
        logger.info(f"Transcription request: format={response_format}, language={language}")

        # Check file size
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large: {file_size} bytes (max: {settings.max_upload_size})",
            )

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename or "audio.wav")[1],
            dir="./tmp",
        )
        temp_file.write(file_content)
        temp_file.close()
        audio_path = temp_file.name

        logger.info(f"Audio saved: {audio_path} ({file_size} bytes)")

        try:
            # Parse timestamp granularities
            granularities = None
            if timestamp_granularities:
                granularities = [g.strip() for g in timestamp_granularities.split(",")]

            # Perform transcription
            start_time = time.time()

            result = await asyncio.to_thread(
                stt_service.transcribe,
                audio_path=audio_path,
                language=language,
                response_format=response_format,
                timestamp_granularities=granularities,
                temperature=temperature or 0.0,
            )

            elapsed = time.time() - start_time
            logger.info(f"Transcription completed in {elapsed:.2f}s")

            # Return response
            if response_format == "text":
                return Response(content=result, media_type="text/plain")
            elif response_format in ["srt", "vtt"]:
                media_type = "text/srt" if response_format == "srt" else "text/vtt"
                return Response(content=result, media_type=media_type)
            else:
                return result

        finally:
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
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
