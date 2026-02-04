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

    # Qwen3-TTS Model
    qwen_tts_model: str = Field(
        default="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        description="Qwen3-TTS model name or path",
    )
    qwen_tts_device: str = Field(default="cpu", description="Device (cpu/cuda:0)")
    qwen_tts_speaker: str = Field(default="female_calm", description="Default speaker")

    # HuggingFace
    hf_endpoint: str = Field(
        default="https://hf-mirror.com",
        description="HuggingFace mirror endpoint",
    )


settings = Settings()
