"""
STT Service - Qwen3-ASR Speech-to-Text
Handles audio transcription using Qwen3-ASR-0.6B model
"""

import logging
import os
from typing import Dict, List, Optional, Union

import torch

from app.config import settings

logger = logging.getLogger(__name__)


class QwenASRService:
    """
    Qwen3-ASR Speech-to-Text Service
    Handles model loading, transcription, and format conversion
    """

    def __init__(self):
        self.model = None
        self.model_name = settings.qwen_asr_model
        self.device = settings.qwen_asr_device
        self.max_batch_size = settings.qwen_asr_max_batch_size
        self._is_loaded = False

    def load_model(self) -> None:
        """
        Load Qwen3-ASR model using qwen_asr library
        """
        if self._is_loaded:
            logger.info("Qwen3-ASR model already loaded")
            return

        try:
            logger.info(f"Loading Qwen3-ASR model: {self.model_name}")
            logger.info(f"Device: {self.device}")

            # Import qwen_asr
            try:
                import qwen_asr
            except ImportError:
                raise ImportError(
                    "qwen_asr package not found. Please install it: pip install qwen-asr"
                )

            # Load model using from_pretrained
            # Note: qwen-asr 0.0.6 API requires pretrained_model_name_or_path as first positional arg
            # and does not support backend, dtype, device parameters
            # forced_aligner is disabled (None) to avoid downloading additional models
            self.model = qwen_asr.Qwen3ASRModel.from_pretrained(
                self.model_name,
                forced_aligner=None,
                max_inference_batch_size=self.max_batch_size,
            )

            # Move model to device after initialization
            if hasattr(self.model, "model"):
                self.model.model = self.model.model.to(self.device)

            self._is_loaded = True
            logger.info("Qwen3-ASR model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load Qwen3-ASR model: {e}", exc_info=True)
            self._is_loaded = False
            raise

    def unload_model(self) -> None:
        """
        Unload model and free memory
        """
        if not self._is_loaded:
            logger.info("Qwen3-ASR model not loaded, nothing to unload")
            return

        try:
            logger.info("Unloading Qwen3-ASR model")

            # Delete model
            if self.model is not None:
                del self.model
                self.model = None

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            self._is_loaded = False
            logger.info("Qwen3-ASR model unloaded successfully")

        except Exception as e:
            logger.error(f"Failed to unload Qwen3-ASR model: {e}", exc_info=True)
            raise

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        response_format: str = "json",
        timestamp_granularities: Optional[List[str]] = None,
        temperature: float = 0.0,
    ) -> Union[str, Dict]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (ISO-639-1), None for auto-detection
            response_format: Output format (json, text, srt, vtt, verbose_json)
            timestamp_granularities: List of timestamp types (word, segment)
            temperature: Sampling temperature (0.0 for greedy decoding)

        Returns:
            Transcription result in requested format
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Validate audio file
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Check file size (50MB limit)
            file_size = os.path.getsize(audio_path)
            if file_size > settings.max_upload_size:
                raise ValueError(
                    f"File size ({file_size} bytes) exceeds limit "
                    f"({settings.max_upload_size} bytes)"
                )

            logger.info(f"Transcribing audio: {audio_path}")

            # Perform transcription
            # Note: qwen-asr 0.0.6 transcribe() only accepts audio, context, language, and return_time_stamps parameters
            # If language is not specified, default to "Chinese" for better results
            transcribe_language = language if language else "Chinese"

            result = self.model.transcribe(
                audio=audio_path,
                language=transcribe_language,
            )

            # qwen-asr 0.0.6 returns a list of ASRTranscription objects
            if isinstance(result, list):
                # Extract text from ASRTranscription objects
                text_parts = []
                for item in result:
                    if hasattr(item, "text"):
                        text_parts.append(item.text)
                    elif isinstance(item, dict):
                        text_parts.append(item.get("text", ""))
                    else:
                        text_parts.append(str(item))
                text = " ".join(text_parts)
                result = {"text": text}
            elif hasattr(result, "text"):
                # Single ASRTranscription object
                result = {"text": result.text}

            # Process result based on response format
            if response_format == "text":
                return result.get("text", "")

            elif response_format == "json":
                return {"text": result.get("text", "")}

            elif response_format == "verbose_json":
                # Build verbose response
                response = {
                    "task": "transcribe",
                    "language": language or "unknown",
                    "text": result.get("text", ""),
                }
                return response

            elif response_format in ["srt", "vtt"]:
                # SRT/VTT not supported yet
                return result.get("text", "")

            else:
                raise ValueError(f"Unsupported response format: {response_format}")

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._is_loaded
