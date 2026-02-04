"""
Audio Router - Proxy to STT/TTS services
"""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class EmotionConfig(BaseModel):
    """Emotion configuration"""

    mode: str = Field(default="auto")
    alpha: float = Field(default=1.0)
    audio: Optional[str] = None
    vector: Optional[list] = None
    text: Optional[str] = None


class TTSRequest(BaseModel):
    """TTS request model"""

    model: str = Field(default="indextts-2")
    input: str = Field(..., min_length=1, max_length=4096)
    voice: str
    response_format: str = Field(default="wav")
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    emotion: Optional[EmotionConfig] = None


@router.post("/transcriptions")
async def create_transcription(
    file: UploadFile = File(...),
    model: str = Form(default="qwen3-asr"),
    language: Optional[str] = Form(default=None),
    response_format: str = Form(default="json"),
    timestamp_granularities: Optional[str] = Form(default=None),
    temperature: Optional[float] = Form(default=0.0),
):
    """
    Transcribe audio to text (OpenAI-compatible)

    Proxies request to STT service
    """
    try:
        logger.info(f"Transcription request: model={model}, format={response_format}")

        # Read file content
        file_content = await file.read()

        # Prepare form data
        files = {"file": (file.filename, file_content, file.content_type)}
        data = {
            "language": language,
            "response_format": response_format,
            "timestamp_granularities": timestamp_granularities,
            "temperature": temperature,
        }

        # Forward to STT service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.stt_service_url}/transcribe",
                files=files,
                data=data,
                timeout=settings.stt_timeout,
            )

        # Return response
        if response.status_code == 200:
            if response_format == "text":
                return Response(content=response.content, media_type="text/plain")
            elif response_format in ["srt", "vtt"]:
                media_type = "text/srt" if response_format == "srt" else "text/vtt"
                return Response(content=response.content, media_type=media_type)
            else:
                return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else {"error": "STT service error"},
            )

    except httpx.TimeoutException:
        logger.error("STT service timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"error": "STT service timeout"},
        )
    except httpx.RequestError as e:
        logger.error(f"STT service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": f"STT service unavailable: {e}"},
        )
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)},
        )


@router.post("/speech")
async def create_speech(request: TTSRequest):
    """
    Generate speech from text (OpenAI-compatible)

    Proxies request to TTS service
    """
    try:
        logger.info(
            f"Speech synthesis request: model={request.model}, "
            f"format={request.response_format}, text_length={len(request.input)}"
        )

        # Map OpenAI-style request to TTS service format
        # Language detection: auto-detect from voice name or text
        language = None
        speaker = request.voice

        # Map common voice names to language codes
        chinese_speakers = ["vivian", "serena", "uncle_fu", "dylan", "eric"]
        english_speakers = ["ryan", "aiden"]
        japanese_speakers = ["ono_anna"]
        korean_speakers = ["sohee"]

        if speaker.lower() in chinese_speakers:
            language = "zh"
        elif speaker.lower() in english_speakers:
            language = "en"
        elif speaker.lower() in japanese_speakers:
            language = "ja"
        elif speaker.lower() in korean_speakers:
            language = "ko"
        # If not matched, let TTS service auto-detect

        # Prepare TTS service request
        tts_request = {
            "input": request.input,
            "speaker": speaker,
            "language": language,
            "response_format": request.response_format,
            "speed": request.speed,
        }

        # Forward to TTS service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.tts_service_url}/synthesize",
                json=tts_request,
                timeout=settings.tts_timeout,
            )

        # Return response
        if response.status_code == 200:
            media_types = {
                "wav": "audio/wav",
                "mp3": "audio/mpeg",
                "flac": "audio/flac",
                "opus": "audio/opus",
            }
            media_type = media_types.get(request.response_format, "audio/wav")

            return Response(
                content=response.content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="speech.{request.response_format}"'
                },
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else {"error": "TTS service error"},
            )

    except httpx.TimeoutException:
        logger.error("TTS service timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"error": "TTS service timeout"},
        )
    except httpx.RequestError as e:
        logger.error(f"TTS service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": f"TTS service unavailable: {e}"},
        )
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)},
        )
