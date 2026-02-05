"""
Model Manager - Intelligent model loading/unloading for GTX 1050 Ti (4GB VRAM)
Ensures only one model is loaded at a time to stay within memory constraints
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Optional

import torch

from app.config import settings

logger = logging.getLogger(__name__)


class ModelState(str, Enum):
    """Model loading states"""

    NONE = "none"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"


class ModelType(str, Enum):
    """Model types"""

    STT = "stt"
    TTS = "tts"
    NONE = "none"


class ModelManager:
    """
    Manages STT and TTS model loading/unloading
    Ensures only one model is loaded at a time due to VRAM constraints
    """

    def __init__(self):
        self._current_model_type: ModelType = ModelType.NONE
        self._model_state: ModelState = ModelState.NONE
        self._stt_service = None
        self._tts_service = None
        self._lock = asyncio.Lock()
        self._request_queue: asyncio.Queue = asyncio.Queue()
        self._switch_timeout = settings.model_switch_timeout
        self._last_switch_time: Optional[float] = None
        self._model_name: Optional[str] = None

    @property
    def current_model_type(self) -> ModelType:
        """Get currently loaded model type"""
        return self._current_model_type

    @property
    def model_state(self) -> ModelState:
        """Get current model state"""
        return self._model_state

    @property
    def model_name(self) -> Optional[str]:
        """Get current model name"""
        return self._model_name

    def get_current_model(self) -> dict:
        """
        Get current model information
        Returns dict with model_type, status, and model_name
        """
        return {
            "model_type": self._current_model_type.value,
            "status": self._model_state.value,
            "model_name": self._model_name,
        }

    async def switch_to_stt(self) -> None:
        """
        Switch to STT model
        Unloads TTS if loaded, then loads STT model
        """
        async with self._lock:
            try:
                logger.info("Switching to STT model")
                start_time = time.time()

                # If STT is already loaded, return
                if (
                    self._current_model_type == ModelType.STT
                    and self._model_state == ModelState.LOADED
                ):
                    logger.info("STT model already loaded")
                    return

                # Unload TTS if loaded
                if self._current_model_type == ModelType.TTS:
                    await self._unload_tts_internal()

                # Load STT
                self._model_state = ModelState.LOADING
                self._current_model_type = ModelType.STT

                # Lazy import to avoid circular dependency
                from app.services.stt_service import QwenASRService

                self._stt_service = QwenASRService()
                await asyncio.wait_for(
                    asyncio.to_thread(self._stt_service.load_model),
                    timeout=self._switch_timeout,
                )

                self._model_state = ModelState.LOADED
                self._model_name = settings.qwen_asr_model
                self._last_switch_time = time.time()

                elapsed = time.time() - start_time
                logger.info(f"STT model loaded successfully in {elapsed:.2f}s")

            except asyncio.TimeoutError:
                logger.error(f"STT model loading timeout after {self._switch_timeout}s")
                self._model_state = ModelState.ERROR
                self._current_model_type = ModelType.NONE
                raise TimeoutError(f"Model loading timeout after {self._switch_timeout}s")
            except Exception as e:
                logger.error(f"Failed to load STT model: {e}", exc_info=True)
                self._model_state = ModelState.ERROR
                self._current_model_type = ModelType.NONE
                raise

    async def unload_stt(self) -> None:
        """
        Unload STT model and free VRAM
        """
        async with self._lock:
            await self._unload_stt_internal()

    async def _unload_stt_internal(self) -> None:
        """Internal method to unload STT (without acquiring lock)"""
        if self._current_model_type != ModelType.STT:
            return

        try:
            logger.info("Unloading STT model")
            self._model_state = ModelState.UNLOADING

            if self._stt_service:
                await asyncio.to_thread(self._stt_service.unload_model)
                self._stt_service = None

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            self._current_model_type = ModelType.NONE
            self._model_state = ModelState.NONE
            self._model_name = None

            logger.info("STT model unloaded successfully")

        except Exception as e:
            logger.error(f"Failed to unload STT model: {e}", exc_info=True)
            self._model_state = ModelState.ERROR
            raise

    async def switch_to_tts(self) -> None:
        """
        Switch to TTS model
        Unloads STT if loaded, then loads TTS model
        """
        async with self._lock:
            try:
                logger.info("Switching to TTS model")
                start_time = time.time()

                # If TTS is already loaded, return
                if (
                    self._current_model_type == ModelType.TTS
                    and self._model_state == ModelState.LOADED
                ):
                    logger.info("TTS model already loaded")
                    return

                # Unload STT if loaded
                if self._current_model_type == ModelType.STT:
                    await self._unload_stt_internal()

                # Load TTS
                self._model_state = ModelState.LOADING
                self._current_model_type = ModelType.TTS

                # Lazy import to avoid circular dependency
                from app.services.tts_service import IndexTTSService

                self._tts_service = IndexTTSService()
                await asyncio.wait_for(
                    asyncio.to_thread(self._tts_service.load_model),
                    timeout=self._switch_timeout,
                )

                self._model_state = ModelState.LOADED
                self._model_name = "indextts-2"
                self._last_switch_time = time.time()

                elapsed = time.time() - start_time
                logger.info(f"TTS model loaded successfully in {elapsed:.2f}s")

            except asyncio.TimeoutError:
                logger.error(f"TTS model loading timeout after {self._switch_timeout}s")
                self._model_state = ModelState.ERROR
                self._current_model_type = ModelType.NONE
                raise TimeoutError(f"Model loading timeout after {self._switch_timeout}s")
            except Exception as e:
                logger.error(f"Failed to load TTS model: {e}", exc_info=True)
                self._model_state = ModelState.ERROR
                self._current_model_type = ModelType.NONE
                raise

    async def unload_tts(self) -> None:
        """
        Unload TTS model and free VRAM
        """
        async with self._lock:
            await self._unload_tts_internal()

    async def _unload_tts_internal(self) -> None:
        """Internal method to unload TTS (without acquiring lock)"""
        if self._current_model_type != ModelType.TTS:
            return

        try:
            logger.info("Unloading TTS model")
            self._model_state = ModelState.UNLOADING

            if self._tts_service:
                await asyncio.to_thread(self._tts_service.unload_model)
                self._tts_service = None

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            self._current_model_type = ModelType.NONE
            self._model_state = ModelState.NONE
            self._model_name = None

            logger.info("TTS model unloaded successfully")

        except Exception as e:
            logger.error(f"Failed to unload TTS model: {e}", exc_info=True)
            self._model_state = ModelState.ERROR
            raise

    def get_stt_service(self):
        """
        Get STT service instance
        Raises RuntimeError if STT is not loaded
        """
        if self._current_model_type != ModelType.STT or self._model_state != ModelState.LOADED:
            raise RuntimeError("STT model is not loaded")
        return self._stt_service

    def get_tts_service(self):
        """
        Get TTS service instance
        Raises RuntimeError if TTS is not loaded
        """
        if self._current_model_type != ModelType.TTS or self._model_state != ModelState.LOADED:
            raise RuntimeError("TTS model is not loaded")
        return self._tts_service

    async def initialize(self) -> None:
        """
        Initialize model manager
        Optionally preload a model based on configuration
        """
        logger.info("Initializing ModelManager")

        if settings.enable_model_preload:
            preload_model = settings.default_preload_model.lower()
            if preload_model == "stt":
                logger.info("Preloading STT model")
                await self.switch_to_stt()
            elif preload_model == "tts":
                logger.info("Preloading TTS model")
                await self.switch_to_tts()
            else:
                logger.info("No model preloading configured")
        else:
            logger.info("Model preloading disabled")

    async def cleanup(self) -> None:
        """
        Cleanup model manager
        Unload all models and free resources
        """
        logger.info("Cleaning up ModelManager")

        if self._current_model_type == ModelType.STT:
            await self.unload_stt()
        elif self._current_model_type == ModelType.TTS:
            await self.unload_tts()

        logger.info("ModelManager cleanup complete")


# Global model manager instance
model_manager = ModelManager()
