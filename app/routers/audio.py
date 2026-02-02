"""
Audio API routes - STT and TTS endpoints
OpenAI-compatible /v1/audio/* endpoints
"""

import asyncio
import logging
import os
import tempfile
import time
from typing import List, Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import Response, StreamingResponse

from app.config import settings
from app.core.model_manager import model_manager
from app.models import (
    ErrorResponse,
    TimestampGranularity,
    TranscriptionResponseFormat,
    TTSRequest,
    TTSResponseFormat,
)
from app.utils import openai_compat

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# STT Endpoint - /v1/audio/transcriptions
# ============================================


@router.post("/transcriptions")
async def create_transcription(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    model: str = Form(default="qwen3-asr-0.6b", description="Model to use"),
    language: Optional[str] = Form(default=None, description="Language code (ISO-639-1)"),
    prompt: Optional[str] = Form(default=None, description="Optional prompt"),
    response_format: str = Form(
        default="json", description="Response format (json/text/srt/vtt/verbose_json)"
    ),
    temperature: Optional[float] = Form(default=0.0, description="Sampling temperature"),
    timestamp_granularities: Optional[str] = Form(
        default=None, description="Comma-separated list: word,segment"
    ),
):
    """
    Transcribe audio to text using Qwen3-ASR

    OpenAI-compatible endpoint for speech-to-text
    """
    try:
        logger.info(f"Transcription request: model={model}, format={response_format}")

        # Validate request parameters
        validation_error = openai_compat.validate_transcription_request(
            model=model,
            language=language,
            response_format=response_format,
            temperature=temperature,
        )
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error.model_dump(),
            )

        # Check file size
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > settings.max_upload_size:
            error = openai_compat.create_file_too_large_error(file_size, settings.max_upload_size)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=error.model_dump(),
            )

        # Save uploaded file to temp location
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename or "audio.wav")[1], dir="./tmp"
        )
        temp_file.write(file_content)
        temp_file.close()
        audio_path = temp_file.name

        logger.info(f"Audio file saved: {audio_path} ({file_size} bytes)")

        try:
            # Switch to STT model
            logger.info("Switching to STT model")
            await model_manager.switch_to_stt()

            # Get STT service
            stt_service = model_manager.get_stt_service()

            # Parse timestamp granularities
            granularities = None
            if timestamp_granularities:
                granularities = [g.strip() for g in timestamp_granularities.split(",")]

            # Perform transcription
            logger.info("Starting transcription")
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

            # Return response based on format
            if response_format == "text":
                return Response(content=result, media_type="text/plain")
            elif response_format in ["srt", "vtt"]:
                media_type = "text/srt" if response_format == "srt" else "text/vtt"
                return Response(content=result, media_type=media_type)
            else:
                # JSON or verbose_json
                return result

        finally:
            # Cleanup temp file
            if os.path.exists(audio_path):
                os.remove(audio_path)

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Model not ready: {e}")
        error = openai_compat.create_model_not_ready_error("stt")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error.model_dump(),
        )
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        error = openai_compat.create_processing_error("transcription", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )


# ============================================
# TTS Endpoint - /v1/audio/speech
# ============================================


@router.post("/speech")
async def create_speech(request: TTSRequest):
    """
    Generate speech from text using IndexTTS2

    OpenAI-compatible endpoint for text-to-speech with voice cloning
    """
    try:
        logger.info(
            f"Speech synthesis request: model={request.model}, "
            f"format={request.response_format}, text_length={len(request.input)}"
        )

        # Validate request parameters
        validation_error = openai_compat.validate_speech_request(
            model=request.model,
            input_text=request.input,
            voice=request.voice,
            response_format=request.response_format,
            speed=request.speed,
        )
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error.model_dump(),
            )

        try:
            # Switch to TTS model
            logger.info("Switching to TTS model")
            await model_manager.switch_to_tts()

            # Get TTS service
            tts_service = model_manager.get_tts_service()

            # Process emotion config
            emotion_config = None
            if request.emotion:
                emotion_config = {
                    "mode": request.emotion.mode,
                    "alpha": request.emotion.alpha,
                }
                if request.emotion.audio:
                    emotion_config["audio"] = request.emotion.audio
                if request.emotion.vector:
                    emotion_config["vector"] = request.emotion.vector
                if request.emotion.text:
                    emotion_config["text"] = request.emotion.text

            # Perform synthesis
            logger.info("Starting speech synthesis")
            start_time = time.time()

            audio_bytes = await asyncio.to_thread(
                tts_service.synthesize,
                text=request.input,
                voice_reference=request.voice,
                response_format=request.response_format,
                speed=request.speed,
                emotion_config=emotion_config,
            )

            elapsed = time.time() - start_time
            logger.info(
                f"Speech synthesis completed in {elapsed:.2f}s, "
                f"output size: {len(audio_bytes)} bytes"
            )

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

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}", exc_info=True)
            error = openai_compat.create_processing_error("speech synthesis", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error.model_dump(),
            )

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Model not ready: {e}")
        error = openai_compat.create_model_not_ready_error("tts")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error.model_dump(),
        )
    except Exception as e:
        logger.error(f"Request processing failed: {e}", exc_info=True)
        error = openai_compat.create_error_response(
            message=str(e),
            error_type="server_error",
            code="request_failed",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(),
        )
