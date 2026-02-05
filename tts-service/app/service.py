"""
TTS Service - Qwen3-TTS Text-to-Speech
Handles speech synthesis using Qwen3-TTS models
"""

import io
import logging
import re
from typing import List, Optional

import numpy as np
import soundfile as sf
import torch

from app.config import settings

logger = logging.getLogger(__name__)


class Qwen3TTSService:
    """
    Qwen3-TTS Text-to-Speech Service
    Handles model loading and speech synthesis
    """

    def __init__(self):
        self.model = None
        self.model_name = settings.qwen_tts_model
        self.device = settings.qwen_tts_device
        self.default_speaker = settings.qwen_tts_speaker
        self.chunk_size = settings.qwen_tts_chunk_size
        self._is_loaded = False

    def load_model(self) -> None:
        """
        Load Qwen3-TTS model
        """
        if self._is_loaded:
            logger.info("Qwen3-TTS model already loaded")
            return

        try:
            logger.info(f"Loading Qwen3-TTS model: {self.model_name}")
            logger.info(f"Device: {self.device}")

            # Import qwen_tts
            try:
                from qwen_tts import Qwen3TTSModel
            except ImportError:
                raise ImportError(
                    "qwen-tts package not found. Please install it: pip install qwen-tts"
                )

            # Load model
            self.model = Qwen3TTSModel.from_pretrained(
                self.model_name,
                device_map=self.device,
                dtype=torch.bfloat16,
            )

            self._is_loaded = True
            logger.info("Qwen3-TTS model loaded successfully")

            # Log supported speakers and languages
            try:
                speakers = self.model.get_supported_speakers()
                languages = self.model.get_supported_languages()
                logger.info(f"Supported speakers: {speakers}")
                logger.info(f"Supported languages: {languages}")
            except Exception as e:
                logger.warning(f"Could not get supported speakers/languages: {e}")

        except Exception as e:
            logger.error(f"Failed to load Qwen3-TTS model: {e}", exc_info=True)
            self._is_loaded = False
            raise

    def unload_model(self) -> None:
        """
        Unload model and free memory
        """
        if not self._is_loaded:
            logger.info("Qwen3-TTS model not loaded, nothing to unload")
            return

        try:
            logger.info("Unloading Qwen3-TTS model")

            # Delete model
            if self.model is not None:
                del self.model
                self.model = None

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            self._is_loaded = False
            logger.info("Qwen3-TTS model unloaded successfully")

        except Exception as e:
            logger.error(f"Failed to unload Qwen3-TTS model: {e}", exc_info=True)
            raise

    def _split_text_into_chunks(self, text: str, max_chunk_size: int) -> List[str]:
        """
        Split long text into smaller chunks at sentence boundaries

        Args:
            text: Input text to split
            max_chunk_size: Maximum characters per chunk

        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]

        # Split by common sentence delimiters (Chinese and English)
        # 按中英文标点符号分句
        sentence_delimiters = r"([。！？；.!?;])"
        sentences = re.split(sentence_delimiters, text)

        # Recombine sentences with their delimiters
        combined_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                combined_sentences.append(sentences[i] + sentences[i + 1])
            else:
                combined_sentences.append(sentences[i])

        # Group sentences into chunks
        chunks = []
        current_chunk = ""

        for sentence in combined_sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        logger.info(f"Split text ({len(text)} chars) into {len(chunks)} chunks")
        return chunks

    def synthesize(
        self,
        text: str,
        speaker: Optional[str] = None,
        language: Optional[str] = None,
        response_format: str = "wav",
        speed: float = 1.0,
    ) -> bytes:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize
            speaker: Speaker name (e.g., 'female_calm', 'male_energetic')
            language: Language code (e.g., 'zh', 'en')
            response_format: Output format (wav, mp3, flac, opus)
            speed: Speech speed (0.25-4.0)

        Returns:
            Audio bytes in requested format
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Use default speaker if not specified
            if speaker is None:
                speaker = self.default_speaker

            # Auto-detect language if not specified
            if language is None:
                # Simple language detection based on text
                if any("\u4e00" <= char <= "\u9fff" for char in text):
                    language = "chinese"
                else:
                    language = "english"

            # Map common language codes to qwen_tts format
            language_map = {
                "zh": "chinese",
                "zh-CN": "chinese",
                "zh-TW": "chinese",
                "en": "english",
                "en-US": "english",
                "en-GB": "english",
                "ja": "japanese",
                "ko": "korean",
                "fr": "french",
                "de": "german",
                "es": "spanish",
                "it": "italian",
                "pt": "portuguese",
                "ru": "russian",
            }
            language = language_map.get(language, language)

            logger.info(
                f"Synthesizing: text_length={len(text)}, speaker={speaker}, "
                f"language={language}, speed={speed}, chunking={'enabled' if self.chunk_size > 0 else 'disabled'}"
            )

            # Check if text needs chunking
            if self.chunk_size > 0 and len(text) > self.chunk_size:
                logger.info(
                    f"Text exceeds chunk size ({len(text)} > {self.chunk_size}), using chunked synthesis"
                )
                return self._synthesize_chunked(text, speaker, language, response_format, speed)

            # Generate speech for single chunk
            # Qwen3-TTS returns (wavs_list, sample_rate) where wavs_list is a list of numpy arrays
            wavs, sample_rate = self.model.generate_custom_voice(
                text=text,
                speaker=speaker,
                language=language,
            )

            # Get the first audio from the list
            audio_data = wavs[0] if isinstance(wavs, list) else wavs

            # Apply speed adjustment if needed
            if speed != 1.0:
                logger.info(f"Applying speed adjustment: {speed}x")
                # Simple speed adjustment by resampling
                try:
                    import librosa

                    audio_data = librosa.effects.time_stretch(audio_data, rate=speed)
                except ImportError:
                    logger.warning("librosa not available, skipping speed adjustment")

            # Convert to bytes
            audio_bytes = self._audio_to_bytes(audio_data, sample_rate, response_format)

            logger.info(f"Synthesis completed: {len(audio_bytes)} bytes")
            return audio_bytes

        except Exception as e:
            logger.error(f"Synthesis failed: {e}", exc_info=True)
            raise

    def _synthesize_chunked(
        self,
        text: str,
        speaker: str,
        language: str,
        response_format: str,
        speed: float,
    ) -> bytes:
        """
        Synthesize long text by splitting into chunks

        Args:
            text: Long text to synthesize
            speaker: Speaker name
            language: Language code
            response_format: Output format
            speed: Speech speed

        Returns:
            Combined audio bytes
        """
        # Split text into chunks
        chunks = self._split_text_into_chunks(text, self.chunk_size)

        # Synthesize each chunk
        audio_chunks = []
        sample_rate = None

        for i, chunk in enumerate(chunks):
            logger.info(f"Synthesizing chunk {i + 1}/{len(chunks)}: {len(chunk)} chars")

            # Generate speech for this chunk
            wavs, sr = self.model.generate_custom_voice(
                text=chunk,
                speaker=speaker,
                language=language,
            )

            # Get audio data
            audio_data = wavs[0] if isinstance(wavs, list) else wavs

            # Apply speed adjustment if needed
            if speed != 1.0:
                try:
                    import librosa

                    audio_data = librosa.effects.time_stretch(audio_data, rate=speed)
                except ImportError:
                    pass

            audio_chunks.append(audio_data)
            if sample_rate is None:
                sample_rate = sr

        # Concatenate all audio chunks
        logger.info(f"Concatenating {len(audio_chunks)} audio chunks")
        combined_audio = np.concatenate(audio_chunks)

        # Convert to bytes (sample_rate should be set from first chunk)
        if sample_rate is None:
            raise RuntimeError("Failed to get sample rate from audio chunks")

        audio_bytes = self._audio_to_bytes(combined_audio, sample_rate, response_format)

        logger.info(f"Chunked synthesis completed: {len(audio_bytes)} bytes")
        return audio_bytes

    def _audio_to_bytes(self, audio_data, sample_rate: int, format: str = "wav") -> bytes:
        """
        Convert audio numpy array to bytes

        Args:
            audio_data: Audio numpy array
            sample_rate: Sample rate
            format: Output format (wav, mp3, flac, opus)

        Returns:
            Audio bytes
        """
        try:
            # Create in-memory buffer
            buffer = io.BytesIO()

            # Write audio to buffer
            if format == "wav":
                sf.write(buffer, audio_data, sample_rate, format="WAV")
            elif format == "flac":
                sf.write(buffer, audio_data, sample_rate, format="FLAC")
            elif format == "mp3":
                # For MP3, we need to use pydub or similar
                # For now, convert to WAV and let the client handle conversion
                logger.warning("MP3 format not directly supported, using WAV")
                sf.write(buffer, audio_data, sample_rate, format="WAV")
            elif format == "opus":
                # For Opus, we need to use pydub or similar
                logger.warning("Opus format not directly supported, using WAV")
                sf.write(buffer, audio_data, sample_rate, format="WAV")
            else:
                # Default to WAV
                sf.write(buffer, audio_data, sample_rate, format="WAV")

            # Get bytes
            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}", exc_info=True)
            raise

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._is_loaded
