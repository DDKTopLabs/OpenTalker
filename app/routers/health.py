"""
Health check and monitoring endpoints
"""

import logging
import time

from fastapi import APIRouter

from app.core.gpu_monitor import gpu_monitor
from app.core.model_manager import model_manager
from app.models import (
    AvailableModel,
    GPUInfo,
    HealthResponse,
    ModelInfo,
    ModelsResponse,
)
from app.utils.openai_compat import get_supported_models

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns service health status, GPU info, and current model status
    """
    try:
        # Get GPU memory info
        gpu_memory = gpu_monitor.get_gpu_memory()
        gpu_info_data = gpu_monitor.get_gpu_info()

        gpu_info = None
        if gpu_info_data.get("available"):
            gpu_info = GPUInfo(
                device_name=gpu_info_data.get("device_name", "Unknown"),
                total_memory_mb=gpu_memory.get("total_mb", 0.0),
                used_memory_mb=gpu_memory.get("used_mb", 0.0),
                free_memory_mb=gpu_memory.get("free_mb", 0.0),
                utilization_percent=gpu_memory.get("utilization_percent", 0.0),
            )

        # Get model info
        model_info_dict = model_manager.get_current_model()
        model_info = ModelInfo(
            model_type=model_info_dict["model_type"],
            status=model_info_dict["status"],
            model_name=model_info_dict["model_name"],
        )

        # Determine overall health status
        health_status = "healthy"
        if model_manager.model_state == "error":
            health_status = "unhealthy"

        return HealthResponse(
            status=health_status,
            gpu=gpu_info,
            model=model_info,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            gpu=None,
            model=ModelInfo(
                model_type="none",
                status="error",
                model_name=None,
            ),
        )


@router.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    """
    List available models

    OpenAI-compatible endpoint for listing models
    """
    try:
        supported = get_supported_models()

        models = []

        # Add transcription models
        for model in supported.get("transcription", []):
            models.append(
                AvailableModel(
                    id=model["id"],
                    object="model",
                    created=int(time.time()),
                    owned_by="qwen",
                )
            )

        # Add speech models
        for model in supported.get("speech", []):
            models.append(
                AvailableModel(
                    id=model["id"],
                    object="model",
                    created=int(time.time()),
                    owned_by="indextts",
                )
            )

        return ModelsResponse(
            object="list",
            data=models,
        )

    except Exception as e:
        logger.error(f"Failed to list models: {e}", exc_info=True)
        return ModelsResponse(
            object="list",
            data=[],
        )


@router.get("/metrics")
async def get_metrics():
    """
    Get performance metrics

    Returns detailed performance statistics and GPU monitoring data
    """
    try:
        # Get performance stats
        perf_stats = gpu_monitor.get_performance_stats()

        # Get GPU info
        gpu_memory = gpu_monitor.get_gpu_memory()
        gpu_info = gpu_monitor.get_gpu_info()

        # Get model info
        model_info = model_manager.get_current_model()

        # Check for memory leaks
        leak_info = gpu_monitor.detect_memory_leak()

        return {
            "timestamp": time.time(),
            "gpu": {
                "available": gpu_info.get("available", False),
                "device_name": gpu_info.get("device_name", "Unknown"),
                "cuda_version": gpu_info.get("cuda_version"),
                "memory": gpu_memory,
            },
            "model": {
                "current_type": model_info["model_type"],
                "current_status": model_info["status"],
                "current_name": model_info["model_name"],
            },
            "performance": perf_stats,
            "memory_leak_detection": leak_info,
        }

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        return {
            "timestamp": time.time(),
            "error": str(e),
        }
