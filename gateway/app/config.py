"""
Gateway Configuration
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Gateway Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Gateway Service
    gateway_host: str = Field(default="0.0.0.0", description="Gateway host")
    gateway_port: int = Field(default=8000, description="Gateway port")
    log_level: str = Field(default="INFO", description="Log level")

    # Backend Services
    stt_service_url: str = Field(
        default="http://localhost:8001",
        description="STT service URL",
    )
    tts_service_url: str = Field(
        default="http://localhost:8002",
        description="TTS service URL",
    )

    # Timeouts
    stt_timeout: int = Field(default=120, description="STT request timeout (seconds)")
    tts_timeout: int = Field(default=180, description="TTS request timeout (seconds)")


settings = Settings()
