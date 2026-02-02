"""
Sample test file demonstrating GPU test markers.

Tests marked with @pytest.mark.gpu will be skipped in CI environments.
"""

import pytest


class TestHealthEndpoint:
    """Test health check endpoint (no GPU required)."""

    def test_health_check_structure(self):
        """Test that health check returns expected structure."""
        # This test doesn't require GPU
        assert True


class TestSTTService:
    """Test STT service."""

    def test_audio_format_validation(self):
        """Test audio format validation (no GPU required)."""
        # This test doesn't require GPU
        assert True

    @pytest.mark.gpu
    def test_transcription_accuracy(self):
        """Test transcription accuracy (requires GPU)."""
        # This test requires GPU and will be skipped in CI
        pytest.skip("GPU required")


class TestTTSService:
    """Test TTS service."""

    def test_text_validation(self):
        """Test text input validation (no GPU required)."""
        # This test doesn't require GPU
        assert True

    @pytest.mark.gpu
    def test_speech_synthesis(self):
        """Test speech synthesis (requires GPU)."""
        # This test requires GPU and will be skipped in CI
        pytest.skip("GPU required")


class TestModelManager:
    """Test model manager."""

    def test_model_switching_logic(self):
        """Test model switching logic (no GPU required)."""
        # This test doesn't require GPU
        assert True

    @pytest.mark.gpu
    @pytest.mark.slow
    def test_model_loading(self):
        """Test actual model loading (requires GPU, slow)."""
        # This test requires GPU and is slow
        pytest.skip("GPU required")
