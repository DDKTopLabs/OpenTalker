"""
Pydantic models for request/response validation
OpenAI-compatible API schemas
"""

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ============================================
# STT (Speech-to-Text) Models
# ============================================


class TranscriptionResponseFormat(str, Enum):
    """Response format for transcription"""

    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VTT = "vtt"
    VERBOSE_JSON = "verbose_json"


class TimestampGranularity(str, Enum):
    """Timestamp granularity for transcription"""

    WORD = "word"
    SEGMENT = "segment"


class TranscriptionRequest(BaseModel):
    """Request model for /v1/audio/transcriptions"""

    model: str = Field(
        default="qwen3-asr-0.6b",
        description="Model to use for transcription",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language of the audio (ISO-639-1 format)",
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Optional text to guide the model's style",
    )
    response_format: TranscriptionResponseFormat = Field(
        default=TranscriptionResponseFormat.JSON,
        description="Format of the transcript output",
    )
    temperature: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Sampling temperature",
    )
    timestamp_granularities: Optional[List[TimestampGranularity]] = Field(
        default=None,
        description="Timestamp granularities to include",
    )


class TranscriptionWord(BaseModel):
    """Word-level timestamp"""

    word: str = Field(description="The transcribed word")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")


class TranscriptionSegment(BaseModel):
    """Segment-level transcription"""

    id: int = Field(description="Segment ID")
    seek: int = Field(description="Seek position")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    text: str = Field(description="Transcribed text")
    tokens: List[int] = Field(description="Token IDs")
    temperature: float = Field(description="Temperature used")
    avg_logprob: float = Field(description="Average log probability")
    compression_ratio: float = Field(description="Compression ratio")
    no_speech_prob: float = Field(description="No speech probability")


class TranscriptionResponse(BaseModel):
    """Response model for transcription (JSON format)"""

    text: str = Field(description="The transcribed text")


class VerboseTranscriptionResponse(BaseModel):
    """Response model for verbose transcription"""

    task: str = Field(default="transcribe", description="Task type")
    language: str = Field(description="Detected or specified language")
    duration: float = Field(description="Audio duration in seconds")
    text: str = Field(description="The transcribed text")
    segments: Optional[List[TranscriptionSegment]] = Field(
        default=None,
        description="Segment-level transcription",
    )
    words: Optional[List[TranscriptionWord]] = Field(
        default=None,
        description="Word-level timestamps",
    )


# ============================================
# TTS (Text-to-Speech) Models
# ============================================


class TTSResponseFormat(str, Enum):
    """Response format for TTS"""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OPUS = "opus"


class EmotionMode(str, Enum):
    """Emotion control mode for TTS"""

    AUTO = "auto"
    AUDIO = "audio"
    VECTOR = "vector"
    TEXT = "text"


class EmotionConfig(BaseModel):
    """Emotion configuration for TTS"""

    mode: EmotionMode = Field(
        default=EmotionMode.AUTO,
        description="Emotion control mode",
    )
    audio: Optional[str] = Field(
        default=None,
        description="Base64-encoded reference audio for emotion",
    )
    vector: Optional[List[float]] = Field(
        default=None,
        description="Emotion vector",
    )
    text: Optional[str] = Field(
        default=None,
        description="Text description of emotion",
    )
    alpha: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Emotion strength (0.0-1.0)",
    )


class TTSRequest(BaseModel):
    """Request model for /v1/audio/speech"""

    model: str = Field(
        default="indextts-2",
        description="Model to use for TTS",
    )
    input: str = Field(
        description="Text to synthesize",
        min_length=1,
        max_length=4096,
    )
    voice: str = Field(
        description="Base64-encoded reference audio for voice cloning",
    )
    response_format: TTSResponseFormat = Field(
        default=TTSResponseFormat.WAV,
        description="Audio format",
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="Speed of the generated audio",
    )
    emotion: Optional[EmotionConfig] = Field(
        default=None,
        description="Emotion configuration",
    )


# ============================================
# Health and Monitoring Models
# ============================================


class ModelStatus(str, Enum):
    """Model loading status"""

    NONE = "none"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"


class GPUInfo(BaseModel):
    """GPU information"""

    device_name: str = Field(description="GPU device name")
    total_memory_mb: float = Field(description="Total GPU memory in MB")
    used_memory_mb: float = Field(description="Used GPU memory in MB")
    free_memory_mb: float = Field(description="Free GPU memory in MB")
    utilization_percent: float = Field(description="GPU memory utilization percentage")


class ModelInfo(BaseModel):
    """Model information"""

    model_type: Literal["stt", "tts", "none"] = Field(description="Type of loaded model")
    status: ModelStatus = Field(description="Model loading status")
    model_name: Optional[str] = Field(default=None, description="Model identifier")


class HealthResponse(BaseModel):
    """Health check response"""

    status: Literal["healthy", "unhealthy"] = Field(description="Service health status")
    gpu: Optional[GPUInfo] = Field(default=None, description="GPU information")
    model: ModelInfo = Field(description="Current model information")


class AvailableModel(BaseModel):
    """Available model information"""

    id: str = Field(description="Model identifier")
    object: str = Field(default="model", description="Object type")
    created: int = Field(description="Creation timestamp")
    owned_by: str = Field(description="Model owner")


class ModelsResponse(BaseModel):
    """Response for /v1/models endpoint"""

    object: str = Field(default="list", description="Object type")
    data: List[AvailableModel] = Field(description="List of available models")


# ============================================
# Error Models
# ============================================


class ErrorDetail(BaseModel):
    """Error detail"""

    message: str = Field(description="Error message")
    type: str = Field(description="Error type")
    param: Optional[str] = Field(default=None, description="Parameter that caused the error")
    code: Optional[str] = Field(default=None, description="Error code")


class ErrorResponse(BaseModel):
    """OpenAI-compatible error response"""

    error: ErrorDetail = Field(description="Error details")
