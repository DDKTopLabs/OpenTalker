"""
Health Router - Health check and service status
"""

import logging

import httpx
from fastapi import APIRouter

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Gateway health check

    Checks status of STT and TTS services
    """
    try:
        stt_status = "unknown"
        tts_status = "unknown"

        # Check STT service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.stt_service_url}/health", timeout=5)
                if response.status_code == 200:
                    stt_data = response.json()
                    stt_status = stt_data.get("status", "unknown")
        except Exception as e:
            logger.warning(f"STT service health check failed: {e}")
            stt_status = "unavailable"

        # Check TTS service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.tts_service_url}/health", timeout=5)
                if response.status_code == 200:
                    tts_data = response.json()
                    tts_status = tts_data.get("status", "unknown")
        except Exception as e:
            logger.warning(f"TTS service health check failed: {e}")
            tts_status = "unavailable"

        # Determine overall status
        if stt_status == "healthy" and tts_status == "healthy":
            overall_status = "healthy"
        elif stt_status == "unavailable" and tts_status == "unavailable":
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "gateway": "healthy",
            "services": {
                "stt": {
                    "status": stt_status,
                    "url": settings.stt_service_url,
                },
                "tts": {
                    "status": tts_status,
                    "url": settings.tts_service_url,
                },
            },
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@router.get("/v1/models")
async def list_models():
    """
    List available models (OpenAI-compatible)
    """
    import time

    return {
        "object": "list",
        "data": [
            {
                "id": "qwen3-asr",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "qwen",
            },
            {
                "id": "indextts-2",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "indextts",
            },
        ],
    }
