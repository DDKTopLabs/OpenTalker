"""
OpenAI API compatibility layer
Handles request validation, response formatting, and error responses
"""

import logging
from typing import Any, Dict, Optional

from app.models import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def validate_transcription_request(
    model: str,
    language: Optional[str] = None,
    response_format: str = "json",
    temperature: Optional[float] = None,
) -> Optional[ErrorResponse]:
    """
    Validate transcription request parameters

    Args:
        model: Model identifier
        language: Language code (optional)
        response_format: Response format
        temperature: Sampling temperature (optional)

    Returns:
        ErrorResponse if validation fails, None if valid
    """
    # Validate model
    valid_models = ["qwen3-asr-0.6b", "qwen3-asr"]
    if model not in valid_models:
        return ErrorResponse(
            error=ErrorDetail(
                message=f"Invalid model: {model}. Supported models: {', '.join(valid_models)}",
                type="invalid_request_error",
                param="model",
                code="invalid_model",
            )
        )

    # Validate response format
    valid_formats = ["json", "text", "srt", "vtt", "verbose_json"]
    if response_format not in valid_formats:
        return ErrorResponse(
            error=ErrorDetail(
                message=f"Invalid response_format: {response_format}. "
                f"Supported formats: {', '.join(valid_formats)}",
                type="invalid_request_error",
                param="response_format",
                code="invalid_format",
            )
        )

    # Validate temperature
    if temperature is not None:
        if not 0.0 <= temperature <= 1.0:
            return ErrorResponse(
                error=ErrorDetail(
                    message=f"Invalid temperature: {temperature}. Must be between 0.0 and 1.0",
                    type="invalid_request_error",
                    param="temperature",
                    code="invalid_value",
                )
            )

    # Validate language (if provided)
    if language is not None:
        # ISO-639-1 codes are 2 characters
        if len(language) != 2:
            return ErrorResponse(
                error=ErrorDetail(
                    message=f"Invalid language code: {language}. Must be ISO-639-1 format (2 chars)",
                    type="invalid_request_error",
                    param="language",
                    code="invalid_language",
                )
            )

    return None


def validate_speech_request(
    model: str,
    input_text: str,
    voice: str,
    response_format: str = "wav",
    speed: float = 1.0,
) -> Optional[ErrorResponse]:
    """
    Validate speech synthesis request parameters

    Args:
        model: Model identifier
        input_text: Text to synthesize
        voice: Voice reference (base64)
        response_format: Audio format
        speed: Speech speed

    Returns:
        ErrorResponse if validation fails, None if valid
    """
    # Validate model
    valid_models = ["indextts-2", "indextts"]
    if model not in valid_models:
        return ErrorResponse(
            error=ErrorDetail(
                message=f"Invalid model: {model}. Supported models: {', '.join(valid_models)}",
                type="invalid_request_error",
                param="model",
                code="invalid_model",
            )
        )

    # Validate input text
    if not input_text or len(input_text.strip()) == 0:
        return ErrorResponse(
            error=ErrorDetail(
                message="Input text cannot be empty",
                type="invalid_request_error",
                param="input",
                code="invalid_value",
            )
        )

    if len(input_text) > 4096:
        return ErrorResponse(
            error=ErrorDetail(
                message=f"Input text too long: {len(input_text)} chars. Maximum is 4096 chars",
                type="invalid_request_error",
                param="input",
                code="text_too_long",
            )
        )

    # Validate voice
    if not voice or len(voice.strip()) == 0:
        return ErrorResponse(
            error=ErrorDetail(
                message="Voice reference is required",
                type="invalid_request_error",
                param="voice",
                code="missing_voice",
            )
        )

    # Validate response format
    valid_formats = ["wav", "mp3", "flac", "opus"]
    if response_format not in valid_formats:
        return ErrorResponse(
            error=ErrorDetail(
                message=f"Invalid response_format: {response_format}. "
                f"Supported formats: {', '.join(valid_formats)}",
                type="invalid_request_error",
                param="response_format",
                code="invalid_format",
            )
        )

    # Validate speed
    if not 0.25 <= speed <= 4.0:
        return ErrorResponse(
            error=ErrorDetail(
                message=f"Invalid speed: {speed}. Must be between 0.25 and 4.0",
                type="invalid_request_error",
                param="speed",
                code="invalid_value",
            )
        )

    return None


def format_transcription_response(
    text: str,
    response_format: str,
    language: Optional[str] = None,
    duration: Optional[float] = None,
    segments: Optional[list] = None,
    words: Optional[list] = None,
) -> Any:
    """
    Format transcription response in OpenAI-compatible format

    Args:
        text: Transcribed text
        response_format: Desired format (json, text, srt, vtt, verbose_json)
        language: Detected/specified language
        duration: Audio duration
        segments: Segment-level transcription
        words: Word-level timestamps

    Returns:
        Formatted response
    """
    if response_format == "text":
        return text

    elif response_format == "json":
        return {"text": text}

    elif response_format == "verbose_json":
        response = {
            "task": "transcribe",
            "language": language or "unknown",
            "duration": duration or 0.0,
            "text": text,
        }
        if segments:
            response["segments"] = segments
        if words:
            response["words"] = words
        return response

    elif response_format in ["srt", "vtt"]:
        # These are already formatted as strings
        return text

    else:
        # Default to JSON
        return {"text": text}


def create_error_response(
    message: str,
    error_type: str = "invalid_request_error",
    param: Optional[str] = None,
    code: Optional[str] = None,
) -> ErrorResponse:
    """
    Create OpenAI-compatible error response

    Args:
        message: Error message
        error_type: Error type (invalid_request_error, server_error, etc.)
        param: Parameter that caused the error
        code: Error code

    Returns:
        ErrorResponse object
    """
    return ErrorResponse(
        error=ErrorDetail(
            message=message,
            type=error_type,
            param=param,
            code=code,
        )
    )


def create_file_too_large_error(file_size: int, max_size: int) -> ErrorResponse:
    """
    Create error response for file too large

    Args:
        file_size: Actual file size in bytes
        max_size: Maximum allowed size in bytes

    Returns:
        ErrorResponse object
    """
    return create_error_response(
        message=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
        error_type="invalid_request_error",
        param="file",
        code="file_too_large",
    )


def create_invalid_audio_error(reason: str) -> ErrorResponse:
    """
    Create error response for invalid audio file

    Args:
        reason: Reason why audio is invalid

    Returns:
        ErrorResponse object
    """
    return create_error_response(
        message=f"Invalid audio file: {reason}",
        error_type="invalid_request_error",
        param="file",
        code="invalid_audio",
    )


def create_model_not_ready_error(model_type: str) -> ErrorResponse:
    """
    Create error response for model not ready

    Args:
        model_type: Type of model (stt/tts)

    Returns:
        ErrorResponse object
    """
    return create_error_response(
        message=f"{model_type.upper()} model is not ready. Please try again later.",
        error_type="server_error",
        code="model_not_ready",
    )


def create_model_loading_error(model_type: str, error: str) -> ErrorResponse:
    """
    Create error response for model loading failure

    Args:
        model_type: Type of model (stt/tts)
        error: Error message

    Returns:
        ErrorResponse object
    """
    return create_error_response(
        message=f"Failed to load {model_type.upper()} model: {error}",
        error_type="server_error",
        code="model_loading_failed",
    )


def create_processing_error(operation: str, error: str) -> ErrorResponse:
    """
    Create error response for processing failure

    Args:
        operation: Operation that failed (transcription/synthesis)
        error: Error message

    Returns:
        ErrorResponse object
    """
    return create_error_response(
        message=f"{operation.capitalize()} failed: {error}",
        error_type="server_error",
        code="processing_failed",
    )


def check_api_version_compatibility(version: Optional[str] = None) -> bool:
    """
    Check API version compatibility

    Args:
        version: API version string (e.g., "v1")

    Returns:
        True if compatible, False otherwise
    """
    # Currently only support v1
    if version is None or version == "v1":
        return True
    return False


def get_supported_models() -> Dict[str, list]:
    """
    Get list of supported models

    Returns:
        Dict with model types and their supported models
    """
    return {
        "transcription": [
            {
                "id": "qwen3-asr-0.6b",
                "name": "Qwen3-ASR-0.6B",
                "type": "speech-to-text",
                "description": "Qwen3 ASR model optimized for GTX 1050 Ti",
            }
        ],
        "speech": [
            {
                "id": "indextts-2",
                "name": "IndexTTS2",
                "type": "text-to-speech",
                "description": "IndexTTS2 with voice cloning and emotion control",
            }
        ],
    }
