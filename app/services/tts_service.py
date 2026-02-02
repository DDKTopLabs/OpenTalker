"""
TTS Service - IndexTTS2 Text-to-Speech
Handles speech synthesis with voice cloning and emotion control
"""

import base64
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import torch

from app.config import settings

logger = logging.getLogger(__name__)


class IndexTTSService:
    """
    IndexTTS2 Text-to-Speech Service
    Handles model loading, speech synthesis, voice cloning, and emotion control
    """

    def __init__(self):
        self.model = None
        self.model_dir = settings.indextts_model_dir
        self.use_fp16 = settings.indextts_use_fp16
        self.use_cuda_kernel = settings.indextts_use_cuda_kernel
        self.use_deepspeed = settings.indextts_use_deepspeed
        self._is_loaded = False

    def load_model(self) -> None:
        """
        Load IndexTTS2 model
        """
        if self._is_loaded:
            logger.info("IndexTTS2 model already loaded")
            return

        try:
            logger.info(f"Loading IndexTTS2 model from: {self.model_dir}")
            logger.info(
                f"FP16: {self.use_fp16}, CUDA kernel: {self.use_cuda_kernel}, "
                f"DeepSpeed: {self.use_deepspeed}"
            )

            # Import IndexTTS2
            try:
                from indextts import IndexTTS2
            except ImportError:
                raise ImportError(
                    "indextts package not found. Please install IndexTTS2 from source."
                )

            # Load model
            self.model = IndexTTS2(
                model_dir=self.model_dir,
                use_fp16=self.use_fp16,
                use_cuda_kernel=self.use_cuda_kernel,
                use_deepspeed=self.use_deepspeed,
            )

            self._is_loaded = True
            logger.info("IndexTTS2 model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load IndexTTS2 model: {e}", exc_info=True)
            self._is_loaded = False
            raise

    def unload_model(self) -> None:
        """
        Unload model and free memory
        """
        if not self._is_loaded:
            logger.info("IndexTTS2 model not loaded, nothing to unload")
            return

        try:
            logger.info("Unloading IndexTTS2 model")

            # Delete model
            if self.model is not None:
                del self.model
                self.model = None

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            self._is_loaded = False
            logger.info("IndexTTS2 model unloaded successfully")

        except Exception as e:
            logger.error(f"Failed to unload IndexTTS2 model: {e}", exc_info=True)
            raise

    def synthesize(
        self,
        text: str,
        voice_reference: str,
        response_format: str = "wav",
        speed: float = 1.0,
        emotion_config: Optional[Dict] = None,
    ) -> bytes:
        """
        Synthesize speech from text

        Args:
            text: Input text to synthesize
            voice_reference: Base64-encoded reference audio for voice cloning
            response_format: Output audio format (wav, mp3, flac, opus)
            speed: Speech speed multiplier (0.25-4.0)
            emotion_config: Emotion control configuration

        Returns:
            Audio data as bytes
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Decode voice reference audio
            logger.info("Decoding voice reference audio")
            ref_audio_path = self._decode_voice_reference(voice_reference)

            # Validate text length
            if len(text) > 4096:
                logger.warning(f"Text length ({len(text)}) exceeds 4096 chars, will segment")

            # Segment text if too long
            text_segments = self._segment_text(text, max_length=1000)
            logger.info(f"Text segmented into {len(text_segments)} parts")

            # Process emotion configuration
            emotion_params = self._process_emotion_config(emotion_config)

            # Synthesize each segment
            audio_segments = []
            for i, segment in enumerate(text_segments):
                logger.info(f"Synthesizing segment {i + 1}/{len(text_segments)}")

                audio = self.model.synthesize(
                    text=segment,
                    reference_audio=ref_audio_path,
                    speed=speed,
                    **emotion_params,
                )

                audio_segments.append(audio)

            # Concatenate audio segments
            if len(audio_segments) > 1:
                logger.info("Concatenating audio segments")
                final_audio = self._concatenate_audio(audio_segments)
            else:
                final_audio = audio_segments[0]

            # Convert to requested format
            audio_bytes = self._convert_audio_format(final_audio, response_format)

            # Cleanup temporary reference audio
            if os.path.exists(ref_audio_path):
                os.remove(ref_audio_path)

            logger.info(f"Speech synthesis complete, output size: {len(audio_bytes)} bytes")
            return audio_bytes

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}", exc_info=True)
            raise

    def _decode_voice_reference(self, voice_reference_b64: str) -> str:
        """
        Decode base64-encoded voice reference audio

        Args:
            voice_reference_b64: Base64-encoded audio data

        Returns:
            Path to temporary audio file
        """
        try:
            # Decode base64
            audio_data = base64.b64decode(voice_reference_b64)

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="./tmp")
            temp_file.write(audio_data)
            temp_file.close()

            logger.info(f"Voice reference saved to: {temp_file.name}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Failed to decode voice reference: {e}")
            raise ValueError(f"Invalid voice reference audio: {e}")

    def _segment_text(self, text: str, max_length: int = 1000) -> List[str]:
        """
        Segment long text into smaller chunks

        Args:
            text: Input text
            max_length: Maximum length per segment

        Returns:
            List of text segments
        """
        if len(text) <= max_length:
            return [text]

        segments = []
        current_segment = ""

        # Split by sentences
        sentences = (
            text.replace("。", "。\n").replace("！", "！\n").replace("？", "？\n").split("\n")
        )

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = sentence

        if current_segment:
            segments.append(current_segment)

        return segments

    def _process_emotion_config(self, emotion_config: Optional[Dict]) -> Dict:
        """
        Process emotion configuration into model parameters

        Args:
            emotion_config: Emotion configuration dict

        Returns:
            Dict of emotion parameters for model
        """
        if not emotion_config:
            return {"emotion_mode": "auto"}

        mode = emotion_config.get("mode", "auto")
        alpha = emotion_config.get("alpha", 1.0)

        params = {
            "emotion_mode": mode,
            "emotion_alpha": alpha,
        }

        if mode == "audio" and "audio" in emotion_config:
            # Decode emotion reference audio
            emotion_audio_b64 = emotion_config["audio"]
            emotion_audio_path = self._decode_voice_reference(emotion_audio_b64)
            params["emotion_audio"] = emotion_audio_path

        elif mode == "vector" and "vector" in emotion_config:
            params["emotion_vector"] = emotion_config["vector"]

        elif mode == "text" and "text" in emotion_config:
            params["emotion_text"] = emotion_config["text"]

        return params

    def _concatenate_audio(self, audio_segments: List) -> any:
        """
        Concatenate multiple audio segments

        Args:
            audio_segments: List of audio arrays/tensors

        Returns:
            Concatenated audio
        """
        try:
            import numpy as np

            # Convert to numpy arrays if needed
            arrays = []
            for audio in audio_segments:
                if isinstance(audio, torch.Tensor):
                    arrays.append(audio.cpu().numpy())
                else:
                    arrays.append(audio)

            # Concatenate
            concatenated = np.concatenate(arrays, axis=-1)
            return concatenated

        except Exception as e:
            logger.error(f"Failed to concatenate audio: {e}")
            raise

    def _convert_audio_format(self, audio_data: any, format: str) -> bytes:
        """
        Convert audio to requested format

        Args:
            audio_data: Audio array/tensor
            format: Target format (wav, mp3, flac, opus)

        Returns:
            Audio bytes in requested format
        """
        try:
            import soundfile as sf
            import io

            # Convert to numpy array if tensor
            if isinstance(audio_data, torch.Tensor):
                audio_array = audio_data.cpu().numpy()
            else:
                audio_array = audio_data

            # Write to bytes buffer
            buffer = io.BytesIO()

            if format == "wav":
                sf.write(buffer, audio_array, samplerate=24000, format="WAV")
            elif format == "flac":
                sf.write(buffer, audio_array, samplerate=24000, format="FLAC")
            elif format == "mp3":
                # For MP3, we need to use ffmpeg
                # First write as WAV, then convert
                temp_wav = io.BytesIO()
                sf.write(temp_wav, audio_array, samplerate=24000, format="WAV")
                temp_wav.seek(0)

                # Convert using ffmpeg (requires ffmpeg-python)
                import ffmpeg

                temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_wav_file.write(temp_wav.read())
                temp_wav_file.close()

                temp_mp3_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_mp3_file.close()

                ffmpeg.input(temp_wav_file.name).output(
                    temp_mp3_file.name, acodec="libmp3lame"
                ).overwrite_output().run(quiet=True)

                with open(temp_mp3_file.name, "rb") as f:
                    buffer.write(f.read())

                os.remove(temp_wav_file.name)
                os.remove(temp_mp3_file.name)

            elif format == "opus":
                # Similar to MP3, use ffmpeg
                temp_wav = io.BytesIO()
                sf.write(temp_wav, audio_array, samplerate=24000, format="WAV")
                temp_wav.seek(0)

                import ffmpeg

                temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_wav_file.write(temp_wav.read())
                temp_wav_file.close()

                temp_opus_file = tempfile.NamedTemporaryFile(delete=False, suffix=".opus")
                temp_opus_file.close()

                ffmpeg.input(temp_wav_file.name).output(
                    temp_opus_file.name, acodec="libopus"
                ).overwrite_output().run(quiet=True)

                with open(temp_opus_file.name, "rb") as f:
                    buffer.write(f.read())

                os.remove(temp_wav_file.name)
                os.remove(temp_opus_file.name)

            else:
                raise ValueError(f"Unsupported audio format: {format}")

            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            logger.error(f"Failed to convert audio format: {e}")
            raise

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._is_loaded
