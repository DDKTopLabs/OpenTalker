"""
Audio processing utilities
Handles format detection, conversion, validation, and subtitle generation
"""

import base64
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# Supported audio formats
SUPPORTED_FORMATS = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "flac": "audio/flac",
    "m4a": "audio/mp4",
    "ogg": "audio/ogg",
    "webm": "audio/webm",
    "opus": "audio/opus",
}


def detect_audio_format(file_path: str) -> Optional[str]:
    """
    Detect audio format from file

    Args:
        file_path: Path to audio file

    Returns:
        Format string (wav, mp3, flac, etc.) or None if unknown
    """
    try:
        # Try by extension first
        ext = Path(file_path).suffix.lower().lstrip(".")
        if ext in SUPPORTED_FORMATS:
            return ext

        # Try using soundfile
        try:
            import soundfile as sf

            info = sf.info(file_path)
            return info.format.lower()
        except Exception:
            pass

        # Try using ffmpeg probe
        try:
            import ffmpeg

            probe = ffmpeg.probe(file_path)
            format_name = probe.get("format", {}).get("format_name", "")
            if "," in format_name:
                format_name = format_name.split(",")[0]
            return format_name.lower()
        except Exception:
            pass

        logger.warning(f"Could not detect format for: {file_path}")
        return None

    except Exception as e:
        logger.error(f"Error detecting audio format: {e}")
        return None


def validate_audio(file_path: str) -> bool:
    """
    Validate audio file

    Args:
        file_path: Path to audio file

    Returns:
        True if valid audio file, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False

        if os.path.getsize(file_path) == 0:
            logger.error(f"File is empty: {file_path}")
            return False

        # Try to detect format
        format = detect_audio_format(file_path)
        if format is None:
            logger.error(f"Unknown audio format: {file_path}")
            return False

        # Try to read audio info
        try:
            import soundfile as sf

            info = sf.info(file_path)
            if info.frames == 0:
                logger.error(f"Audio file has no frames: {file_path}")
                return False
            return True
        except Exception:
            pass

        # Fallback: try ffmpeg probe
        try:
            import ffmpeg

            probe = ffmpeg.probe(file_path)
            streams = probe.get("streams", [])
            audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
            if not audio_streams:
                logger.error(f"No audio streams found: {file_path}")
                return False
            return True
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False

    except Exception as e:
        logger.error(f"Error validating audio: {e}")
        return False


def convert_to_wav(file_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert audio file to WAV format

    Args:
        file_path: Path to input audio file
        output_path: Optional output path, if None creates temp file

    Returns:
        Path to WAV file
    """
    try:
        if output_path is None:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="./tmp")
            output_path = temp_file.name
            temp_file.close()

        logger.info(f"Converting {file_path} to WAV: {output_path}")

        # Try using soundfile first (faster for supported formats)
        try:
            import soundfile as sf

            data, samplerate = sf.read(file_path)
            sf.write(output_path, data, samplerate, format="WAV")
            logger.info("Conversion successful using soundfile")
            return output_path
        except Exception:
            pass

        # Fallback to ffmpeg (handles more formats)
        try:
            import ffmpeg

            (
                ffmpeg.input(file_path)
                .output(output_path, acodec="pcm_s16le", ar=16000, ac=1)
                .overwrite_output()
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
            )
            logger.info("Conversion successful using ffmpeg")
            return output_path
        except Exception as e:
            logger.error(f"FFmpeg conversion failed: {e}")
            raise

    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise ValueError(f"Failed to convert audio to WAV: {e}")


def encode_audio_base64(file_path: str) -> str:
    """
    Encode audio file to base64 string

    Args:
        file_path: Path to audio file

    Returns:
        Base64-encoded string
    """
    try:
        with open(file_path, "rb") as f:
            audio_data = f.read()
        return base64.b64encode(audio_data).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encode audio to base64: {e}")
        raise


def decode_audio_base64(base64_string: str, output_path: Optional[str] = None) -> str:
    """
    Decode base64 string to audio file

    Args:
        base64_string: Base64-encoded audio data
        output_path: Optional output path, if None creates temp file

    Returns:
        Path to decoded audio file
    """
    try:
        audio_data = base64.b64decode(base64_string)

        if output_path is None:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="./tmp")
            output_path = temp_file.name
            temp_file.close()

        with open(output_path, "wb") as f:
            f.write(audio_data)

        return output_path
    except Exception as e:
        logger.error(f"Failed to decode base64 audio: {e}")
        raise ValueError(f"Invalid base64 audio data: {e}")


def format_timestamp_srt(seconds: float) -> str:
    """
    Format timestamp for SRT format (HH:MM:SS,mmm)

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """
    Format timestamp for VTT format (HH:MM:SS.mmm)

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def generate_srt(segments: List[Dict]) -> str:
    """
    Generate SRT subtitle format from segments

    Args:
        segments: List of segment dicts with start, end, text

    Returns:
        SRT formatted string
    """
    try:
        srt_lines = []

        for i, segment in enumerate(segments, start=1):
            start = segment.get("start", 0.0)
            end = segment.get("end", 0.0)
            text = segment.get("text", "").strip()

            if not text:
                continue

            # Segment number
            srt_lines.append(str(i))

            # Timestamp line
            start_time = format_timestamp_srt(start)
            end_time = format_timestamp_srt(end)
            srt_lines.append(f"{start_time} --> {end_time}")

            # Text
            srt_lines.append(text)

            # Blank line
            srt_lines.append("")

        return "\n".join(srt_lines)

    except Exception as e:
        logger.error(f"Failed to generate SRT: {e}")
        raise


def generate_vtt(segments: List[Dict]) -> str:
    """
    Generate VTT subtitle format from segments

    Args:
        segments: List of segment dicts with start, end, text

    Returns:
        VTT formatted string
    """
    try:
        vtt_lines = ["WEBVTT", ""]

        for i, segment in enumerate(segments, start=1):
            start = segment.get("start", 0.0)
            end = segment.get("end", 0.0)
            text = segment.get("text", "").strip()

            if not text:
                continue

            # Timestamp line
            start_time = format_timestamp_vtt(start)
            end_time = format_timestamp_vtt(end)
            vtt_lines.append(f"{start_time} --> {end_time}")

            # Text
            vtt_lines.append(text)

            # Blank line
            vtt_lines.append("")

        return "\n".join(vtt_lines)

    except Exception as e:
        logger.error(f"Failed to generate VTT: {e}")
        raise


def get_audio_duration(file_path: str) -> float:
    """
    Get audio duration in seconds

    Args:
        file_path: Path to audio file

    Returns:
        Duration in seconds
    """
    try:
        # Try soundfile first
        try:
            import soundfile as sf

            info = sf.info(file_path)
            return info.duration
        except Exception:
            pass

        # Fallback to ffmpeg
        try:
            import ffmpeg

            probe = ffmpeg.probe(file_path)
            duration = float(probe.get("format", {}).get("duration", 0.0))
            return duration
        except Exception:
            pass

        logger.warning(f"Could not determine duration for: {file_path}")
        return 0.0

    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0.0


def get_audio_info(file_path: str) -> Dict:
    """
    Get detailed audio file information

    Args:
        file_path: Path to audio file

    Returns:
        Dict with audio information (format, duration, sample_rate, channels)
    """
    try:
        info = {
            "format": detect_audio_format(file_path),
            "duration": 0.0,
            "sample_rate": 0,
            "channels": 0,
            "file_size": os.path.getsize(file_path),
        }

        # Try soundfile
        try:
            import soundfile as sf

            sf_info = sf.info(file_path)
            info["duration"] = sf_info.duration
            info["sample_rate"] = sf_info.samplerate
            info["channels"] = sf_info.channels
            return info
        except Exception:
            pass

        # Fallback to ffmpeg
        try:
            import ffmpeg

            probe = ffmpeg.probe(file_path)
            info["duration"] = float(probe.get("format", {}).get("duration", 0.0))

            audio_streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]
            if audio_streams:
                stream = audio_streams[0]
                info["sample_rate"] = int(stream.get("sample_rate", 0))
                info["channels"] = int(stream.get("channels", 0))

            return info
        except Exception:
            pass

        return info

    except Exception as e:
        logger.error(f"Error getting audio info: {e}")
        return {
            "format": None,
            "duration": 0.0,
            "sample_rate": 0,
            "channels": 0,
            "file_size": 0,
        }
