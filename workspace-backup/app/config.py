"""
Configuration management using Pydantic Settings
Loads configuration from environment variables and .env file
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================
    # HuggingFace Mirror Configuration
    # ============================================
    hf_endpoint: str = Field(
        default="https://hf-mirror.com",
        description="HuggingFace mirror endpoint for model downloads",
    )
    huggingface_hub_cache: str = Field(
        default="./models/.cache/huggingface",
        description="HuggingFace model cache directory",
    )

    # ============================================
    # STT Configuration - Qwen3-ASR
    # ============================================
    qwen_asr_model: str = Field(
        default="Qwen/Qwen3-ASR-0.6B",
        description="Qwen3-ASR model identifier",
    )
    qwen_asr_backend: str = Field(
        default="transformers",
        description="Backend for Qwen3-ASR (transformers or onnx)",
    )
    qwen_asr_dtype: str = Field(
        default="float16",
        description="Data type for model inference (float16 or float32)",
    )
    qwen_asr_device: str = Field(
        default="cuda:0",
        description="Device for model inference",
    )
    qwen_asr_enable_aligner: str = Field(
        default="auto",
        description="Enable forced aligner for timestamp generation",
    )
    qwen_asr_max_batch_size: int = Field(
        default=8,
        description="Maximum batch size for STT processing",
    )

    # ============================================
    # TTS Configuration - IndexTTS2
    # ============================================
    indextts_model_dir: str = Field(
        default="./models/indextts",
        description="IndexTTS2 model directory",
    )
    indextts_use_fp16: bool = Field(
        default=True,
        description="Use FP16 precision for TTS",
    )
    indextts_use_cuda_kernel: bool = Field(
        default=False,
        description="Use CUDA kernel optimization (requires compilation)",
    )
    indextts_use_deepspeed: bool = Field(
        default=False,
        description="Use DeepSpeed for TTS inference",
    )

    # ============================================
    # Service Configuration
    # ============================================
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    max_upload_size: int = Field(
        default=52428800,  # 50MB
        description="Maximum upload file size in bytes",
    )

    # ============================================
    # GPU Configuration
    # ============================================
    cuda_visible_devices: str = Field(
        default="0",
        description="CUDA visible devices",
    )

    # ============================================
    # Model Management
    # ============================================
    model_switch_timeout: int = Field(
        default=30,
        description="Timeout for model switching in seconds",
    )
    enable_model_preload: bool = Field(
        default=False,
        description="Enable model preloading on startup",
    )
    default_preload_model: str = Field(
        default="none",
        description="Default model to preload (none/stt/tts)",
    )


# Global settings instance
settings = Settings()
