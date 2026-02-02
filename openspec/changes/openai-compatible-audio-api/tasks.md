## 1. Project Setup and Configuration

- [ ] 1.1 Create project directory structure (app/, scripts/, tests/, models/)
- [ ] 1.2 Create pyproject.toml with uv configuration and all mirror sources
- [ ] 1.3 Configure tool.uv.sources to pin torch and torchaudio to tsinghua-pytorch index
- [ ] 1.4 Configure tool.uv.index entries for tsinghua-pypi, tsinghua-pytorch, and fallback sources
- [ ] 1.5 Create .python-version file specifying Python 3.11
- [ ] 1.6 Create .env.example with all configuration variables
- [ ] 1.7 Create .dockerignore file
- [ ] 1.8 Create .gitignore file

## 2. Core Application Structure

- [ ] 2.1 Create app/__init__.py
- [ ] 2.2 Create app/main.py with FastAPI application initialization
- [ ] 2.3 Create app/config.py with Pydantic settings management
- [ ] 2.4 Create app/models.py with Pydantic request/response models
- [ ] 2.5 Configure CORS middleware in main.py
- [ ] 2.6 Configure logging in main.py
- [ ] 2.7 Add startup event handler for initialization

## 3. Model Management System

- [ ] 3.1 Create app/core/__init__.py
- [ ] 3.2 Create app/core/model_manager.py with ModelManager class
- [ ] 3.3 Implement ModelManager.switch_to_stt() method
- [ ] 3.4 Implement ModelManager.unload_stt() method
- [ ] 3.5 Implement ModelManager.switch_to_tts() method
- [ ] 3.6 Implement ModelManager.unload_tts() method
- [ ] 3.7 Implement ModelManager.get_current_model() method
- [ ] 3.8 Implement request queue for concurrent request handling
- [ ] 3.9 Add model state tracking (STT, TTS, NONE, LOADING, UNLOADING)
- [ ] 3.10 Add timeout handling for model switches (30s default)

## 4. GPU Monitoring

- [ ] 4.1 Create app/core/gpu_monitor.py
- [ ] 4.2 Implement get_gpu_memory() function using torch.cuda
- [ ] 4.3 Implement get_gpu_info() function (device name, CUDA version, compute capability)
- [ ] 4.4 Implement track_model_switch() function for performance metrics
- [ ] 4.5 Implement get_performance_stats() function
- [ ] 4.6 Add memory leak detection logic
- [ ] 4.7 Add VRAM threshold warnings (90% usage)

## 5. STT Service Implementation

- [ ] 5.1 Create app/services/__init__.py
- [ ] 5.2 Create app/services/stt_service.py with QwenASRService class
- [ ] 5.3 Implement QwenASRService.__init__() with model configuration
- [ ] 5.4 Implement QwenASRService.load_model() using qwen_asr.Qwen3ASRModel.from_pretrained()
- [ ] 5.5 Implement QwenASRService.unload_model() with proper cleanup
- [ ] 5.6 Implement QwenASRService.transcribe() method
- [ ] 5.7 Add audio format validation and conversion
- [ ] 5.8 Add language detection and specification handling
- [ ] 5.9 Add timestamp generation support (segment and word level)
- [ ] 5.10 Add response format conversion (JSON, text, SRT, VTT)
- [ ] 5.11 Add error handling for invalid audio files
- [ ] 5.12 Add file size validation (50MB limit)

## 6. TTS Service Implementation

- [ ] 6.1 Create app/services/tts_service.py with IndexTTSService class
- [ ] 6.2 Implement IndexTTSService.__init__() with model configuration
- [ ] 6.3 Implement IndexTTSService.load_model() using IndexTTS2
- [ ] 6.4 Implement IndexTTSService.unload_model() with proper cleanup
- [ ] 6.5 Implement IndexTTSService.synthesize() method
- [ ] 6.6 Add voice reference audio decoding (base64)
- [ ] 6.7 Add emotion control support (auto, audio, vector, text modes)
- [ ] 6.8 Add emotion alpha parameter handling
- [ ] 6.9 Add text segmentation for long inputs (>1000 chars)
- [ ] 6.10 Add silence interval configuration
- [ ] 6.11 Add streaming support (optional)
- [ ] 6.12 Add error handling for invalid voice references

## 7. Audio Utilities

- [ ] 7.1 Create app/utils/__init__.py
- [ ] 7.2 Create app/utils/audio_utils.py
- [ ] 7.3 Implement audio format detection function
- [ ] 7.4 Implement audio format conversion function (to WAV)
- [ ] 7.5 Implement audio validation function
- [ ] 7.6 Implement base64 audio encoding/decoding functions
- [ ] 7.7 Implement SRT format generation function
- [ ] 7.8 Implement VTT format generation function

## 8. OpenAI Compatibility Layer

- [ ] 8.1 Create app/utils/openai_compat.py
- [ ] 8.2 Implement request format validation for /v1/audio/transcriptions
- [ ] 8.3 Implement request format validation for /v1/audio/speech
- [ ] 8.4 Implement response format conversion to OpenAI schema
- [ ] 8.5 Implement error response formatting (OpenAI-compatible)
- [ ] 8.6 Add API version compatibility checks

## 9. API Routes - STT

- [ ] 9.1 Create app/routers/__init__.py
- [ ] 9.2 Create app/routers/audio.py
- [ ] 9.3 Implement POST /v1/audio/transcriptions endpoint
- [ ] 9.4 Add multipart/form-data file upload handling
- [ ] 9.5 Add model parameter handling (default: qwen3-asr-0.6b)
- [ ] 9.6 Add language parameter handling (optional)
- [ ] 9.7 Add response_format parameter handling (json/text/srt/vtt)
- [ ] 9.8 Add timestamp_granularities parameter handling
- [ ] 9.9 Add temperature parameter handling (optional)
- [ ] 9.10 Integrate with ModelManager for model switching
- [ ] 9.11 Add request timeout handling
- [ ] 9.12 Add proper error responses (400, 413, 503)

## 10. API Routes - TTS

- [ ] 10.1 Implement POST /v1/audio/speech endpoint in audio.py
- [ ] 10.2 Add JSON request body parsing
- [ ] 10.3 Add input text validation
- [ ] 10.4 Add voice parameter handling (base64 audio)
- [ ] 10.5 Add model parameter handling (default: indextts-2)
- [ ] 10.6 Add response_format parameter handling (default: wav)
- [ ] 10.7 Add speed parameter handling (optional)
- [ ] 10.8 Add emotion parameter handling (mode, audio, vector, text, alpha)
- [ ] 10.9 Integrate with ModelManager for model switching
- [ ] 10.10 Add streaming response support
- [ ] 10.11 Add proper error responses (400, 503)

## 11. Health and Monitoring Endpoints

- [ ] 11.1 Create app/routers/health.py
- [ ] 11.2 Implement GET /health endpoint
- [ ] 11.3 Add GPU status to health response (VRAM usage, current model)
- [ ] 11.4 Add model status to health response (loaded, ready, loading)
- [ ] 11.5 Implement GET /v1/models endpoint
- [ ] 11.6 Add available models list to response
- [ ] 11.7 Implement GET /metrics endpoint (optional)
- [ ] 11.8 Add performance statistics to metrics response
- [ ] 11.9 Add model switch statistics to metrics response

## 12. Docker Configuration

- [ ] 12.1 Create Dockerfile based on nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04
- [ ] 12.2 Add Ubuntu APT source replacement to Tsinghua mirror
- [ ] 12.3 Install system dependencies (python3.11, ffmpeg, libsndfile1, etc.)
- [ ] 12.4 Install uv package manager
- [ ] 12.5 Copy pyproject.toml and .python-version
- [ ] 12.6 Run uv pip install to install dependencies
- [ ] 12.7 Copy application code
- [ ] 12.8 Create model cache directories
- [ ] 12.9 Add HEALTHCHECK instruction
- [ ] 12.10 Set CMD to start uvicorn server

## 13. Docker Compose Configuration

- [ ] 13.1 Create docker-compose.yml
- [ ] 13.2 Configure service with GPU support (NVIDIA runtime)
- [ ] 13.3 Add port mapping (8000:8000)
- [ ] 13.4 Add volume mounts for models and temp files
- [ ] 13.5 Add all environment variables
- [ ] 13.6 Configure resource limits (GPU count, memory)
- [ ] 13.7 Add restart policy (unless-stopped)
- [ ] 13.8 Add healthcheck configuration

## 14. Model Download Scripts

- [ ] 14.1 Create scripts/__init__.py
- [ ] 14.2 Create scripts/download_models.sh
- [ ] 14.3 Add HF_ENDPOINT configuration for HF-Mirror
- [ ] 14.4 Add Qwen3-ASR-0.6B download using huggingface-hub
- [ ] 14.5 Add Qwen3-ForcedAligner-0.6B download (optional)
- [ ] 14.6 Add IndexTTS2 model download
- [ ] 14.7 Add download progress reporting
- [ ] 14.8 Add error handling and retry logic
- [ ] 14.9 Create scripts/init_models.py for Python-based initialization
- [ ] 14.10 Add model verification after download

## 15. Testing

- [ ] 15.1 Create tests/__init__.py
- [ ] 15.2 Create tests/test_stt.py
- [ ] 15.3 Add test for STT endpoint with sample audio
- [ ] 15.4 Add test for language detection
- [ ] 15.5 Add test for timestamp generation
- [ ] 15.6 Add test for different response formats
- [ ] 15.7 Create tests/test_tts.py
- [ ] 15.8 Add test for TTS endpoint with sample text
- [ ] 15.9 Add test for voice cloning
- [ ] 15.10 Add test for emotion control modes
- [ ] 15.11 Create tests/test_model_manager.py
- [ ] 15.12 Add test for model switching logic
- [ ] 15.13 Add test for VRAM monitoring
- [ ] 15.14 Add test for concurrent request handling

## 16. Documentation

- [ ] 16.1 Create README.md with project overview
- [ ] 16.2 Add installation instructions (local and Docker)
- [ ] 16.3 Add quick start guide
- [ ] 16.4 Add API endpoint documentation with examples
- [ ] 16.5 Add configuration reference (environment variables)
- [ ] 16.6 Add hardware requirements section
- [ ] 16.7 Add performance expectations section
- [ ] 16.8 Add troubleshooting guide
- [ ] 16.9 Add mirror configuration documentation
- [ ] 16.10 Add CUDA version switching instructions
- [ ] 16.11 Create CONTRIBUTING.md (optional)
- [ ] 16.12 Create LICENSE file

## 17. Integration and Verification

- [ ] 17.1 Test local installation with uv
- [ ] 17.2 Verify all mirror sources are working
- [ ] 17.3 Test Docker build process
- [ ] 17.4 Test Docker container startup
- [ ] 17.5 Verify model downloads complete successfully
- [ ] 17.6 Test STT endpoint with various audio formats
- [ ] 17.7 Test TTS endpoint with various inputs
- [ ] 17.8 Verify model switching works correctly
- [ ] 17.9 Verify VRAM usage stays within 4GB limit
- [ ] 17.10 Test health check endpoints
- [ ] 17.11 Verify OpenAI API compatibility
- [ ] 17.12 Performance testing (measure latencies)
- [ ] 17.13 Load testing (concurrent requests)
- [ ] 17.14 Error scenario testing (invalid inputs, OOM, etc.)

## 18. Deployment Preparation

- [ ] 18.1 Create deployment checklist in README
- [ ] 18.2 Document NVIDIA driver requirements
- [ ] 18.3 Document NVIDIA Container Toolkit setup
- [ ] 18.4 Create example .env file with all variables
- [ ] 18.5 Add Docker registry push instructions (if applicable)
- [ ] 18.6 Add monitoring and logging recommendations
- [ ] 18.7 Add backup and recovery procedures
- [ ] 18.8 Add upgrade procedures
- [ ] 18.9 Create operational runbook
- [ ] 18.10 Add security considerations documentation
