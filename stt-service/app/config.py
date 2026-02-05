"""
STT Service Configuration
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """STT Service Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Service
    service_host: str = Field(default="0.0.0.0", description="Service host")
    service_port: int = Field(default=8001, description="Service port")
    log_level: str = Field(default="INFO", description="Log level")

    # Qwen3-ASR Model
    qwen_asr_model: str = Field(
        default="Qwen/Qwen3-ASR-0.6B",
        description="Qwen3-ASR model path or HF model ID",
    )
    qwen_asr_device: str = Field(default="cuda:0", description="Device (cpu/cuda:0)")
    qwen_asr_max_batch_size: int = Field(default=8, description="Max batch size")
    qwen_asr_use_fp16: bool = Field(
        default=True,
        description="Use FP16 half precision for inference (reduces VRAM by ~50%)",
    )

    # File Upload
    max_upload_size: int = Field(default=52428800, description="Max upload size (50MB)")

    # HuggingFace
    hf_endpoint: str = Field(
        default="https://hf-mirror.com",
        description="HuggingFace mirror endpoint",
    )


settings = Settings()
