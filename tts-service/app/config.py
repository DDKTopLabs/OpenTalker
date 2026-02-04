"""
TTS Service Configuration
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """TTS Service Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Service
    service_host: str = Field(default="0.0.0.0", description="Service host")
    service_port: int = Field(default=8002, description="Service port")
    log_level: str = Field(default="INFO", description="Log level")

    # IndexTTS2 Model
    indextts_model_dir: str = Field(
        default="./models/indextts",
        description="IndexTTS2 model directory",
    )
    indextts_device: str = Field(default="cpu", description="Device (cpu/cuda:0)")
    indextts_use_fp16: bool = Field(default=True, description="Use FP16 precision")

    # HuggingFace
    hf_endpoint: str = Field(
        default="https://hf-mirror.com",
        description="HuggingFace mirror endpoint",
    )


settings = Settings()
