## Context

This project creates an OpenAI-compatible audio processing API service for Chinese mainland users, optimized for entry-level GPUs (GTX 1050 Ti with 4GB VRAM). The service integrates two open-source models: Qwen3-ASR-0.6B for speech-to-text and IndexTTS2 for text-to-speech.

**Current State:**
- No existing audio API service in the codebase
- Target deployment environment: GTX 1050 Ti (CUDA Compute Capability 6.1, 4GB VRAM)
- Network environment: China mainland with restricted access to international services

**Constraints:**
- 4GB VRAM limit requires intelligent model management (cannot load both models simultaneously)
- GTX 1050 Ti does not support vLLM (requires CC 7.0+), must use Transformers backend
- Must use Chinese mirror sources (Tsinghua University) for acceptable download speeds
- Must maintain OpenAI API compatibility for easy integration

**Stakeholders:**
- Individual developers and small teams in China
- Users with entry-level GPU hardware
- Applications requiring offline audio processing capabilities

## Goals / Non-Goals

**Goals:**
- Provide OpenAI-compatible `/v1/audio/transcriptions` and `/v1/audio/speech` endpoints
- Support 52 languages for STT and high-quality Chinese TTS with emotion control
- Operate reliably within 4GB VRAM constraint through intelligent model switching
- Achieve 10x+ faster deployment using Chinese mirror sources
- Deliver acceptable performance: 2-3s for 10s audio (STT), 1-2s for short text (TTS)
- Provide Docker deployment with NVIDIA GPU support

**Non-Goals:**
- Real-time streaming transcription (not supported by Transformers backend)
- Simultaneous STT+TTS processing (VRAM constraint)
- Support for GPUs with <4GB VRAM
- Multi-GPU distribution
- Production-scale high-concurrency serving (optimized for personal/small team use)

## Decisions

### Decision 1: Use Transformers Backend Instead of vLLM

**Choice:** Use Qwen3-ASR with Transformers backend

**Rationale:**
- GTX 1050 Ti has Compute Capability 6.1, but vLLM requires CC 7.0+
- Transformers backend is officially supported by qwen-asr package
- Provides stable, well-documented API
- Acceptable performance for target use case (personal/small team)

**Alternatives Considered:**
- vLLM backend: Not compatible with GTX 1050 Ti hardware
- CPU-only inference: Too slow (5-10x slower than GPU)
- Upgrade hardware requirement: Conflicts with goal of supporting entry-level GPUs

**Trade-offs:**
- ✅ Hardware compatibility
- ✅ Stable and mature
- ❌ No streaming support
- ❌ Lower throughput vs vLLM (but acceptable for target scale)

### Decision 2: Use Qwen3-ASR-0.6B Instead of 1.7B

**Choice:** Use the 0.6B model variant

**Rationale:**
- 0.6B model uses ~2.0-2.3GB VRAM (fits comfortably in 4GB)
- 1.7B model uses ~3.5GB VRAM (leaves insufficient room for TTS model)
- Accuracy difference is minimal: 0.6B achieves 3.44% WER vs 1.7B's 2.88% WER on Chinese
- Faster inference time benefits user experience

**Alternatives Considered:**
- 1.7B model: Better accuracy but incompatible with 4GB VRAM constraint
- Smaller models (base/tiny): Significantly lower accuracy

**Trade-offs:**
- ✅ Fits VRAM constraint
- ✅ Faster inference
- ❌ Slightly lower accuracy (0.56% WER difference)

### Decision 3: Intelligent Model Manager with On-Demand Loading

**Choice:** Implement a ModelManager that loads/unloads models based on request type

**Rationale:**
- Cannot fit both models in 4GB VRAM simultaneously
- Model switching overhead (5-8s) is acceptable for target use case
- Allows using best-quality models for each task
- Prevents OOM errors

**Architecture:**
```python
class ModelManager:
    current_model: Literal["stt", "tts", "none"]
    
    async def switch_to_stt():
        if current_model == "tts":
            unload_tts()
            torch.cuda.empty_cache()
        load_stt()
    
    async def switch_to_tts():
        if current_model == "stt":
            unload_stt()
            torch.cuda.empty_cache()
        load_tts()
```

**Alternatives Considered:**
- Keep both models in RAM, swap to GPU: Too slow, high RAM usage
- Use smaller models to fit both: Unacceptable quality degradation
- CPU fallback for one model: 5-10x slower, poor user experience

**Trade-offs:**
- ✅ Optimal model quality for each task
- ✅ Reliable VRAM management
- ❌ 5-8s latency on first request after model switch
- ❌ Cannot process STT and TTS requests simultaneously

### Decision 4: Use uv with tool.uv.sources for Package Management

**Choice:** Use uv package manager with explicit index pinning via `tool.uv.sources`

**Rationale:**
- uv is 10-100x faster than pip for dependency resolution and installation
- `tool.uv.sources` allows pinning PyTorch packages to Tsinghua mirror
- `explicit = true` prevents dependency confusion attacks
- All configuration centralized in pyproject.toml (version control friendly)

**Configuration:**
```toml
[tool.uv.sources]
torch = { index = "tsinghua-pytorch" }
torchaudio = { index = "tsinghua-pytorch" }

[[tool.uv.index]]
name = "tsinghua-pytorch"
url = "https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cu121"
explicit = true
```

**Alternatives Considered:**
- pip with requirements.txt: 10x slower, less reliable dependency resolution
- conda: Slower, larger environment, less flexible for custom indexes
- Manual wheel downloads: Not reproducible, maintenance burden

**Trade-offs:**
- ✅ 10x faster installation
- ✅ Reproducible builds (uv.lock)
- ✅ Prevents dependency confusion
- ❌ Requires uv installation (additional tool)

### Decision 5: FastAPI with Async Request Handling

**Choice:** Use FastAPI with async/await for API endpoints

**Rationale:**
- Native async support for I/O-bound operations (file uploads, model loading)
- Automatic OpenAPI documentation generation
- Pydantic integration for request/response validation
- Excellent performance for target scale

**Architecture:**
```python
@router.post("/v1/audio/transcriptions")
async def transcribe(file: UploadFile):
    await model_manager.switch_to_stt()
    result = await stt_service.transcribe(file)
    return result
```

**Alternatives Considered:**
- Flask: Simpler but lacks native async support
- Django: Too heavy for this use case
- Raw ASGI: Too low-level, more development time

**Trade-offs:**
- ✅ High performance
- ✅ Modern async patterns
- ✅ Auto-generated docs
- ❌ Slightly steeper learning curve than Flask

### Decision 6: Docker with NVIDIA Container Toolkit

**Choice:** Provide Docker image based on nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

**Rationale:**
- Ensures consistent CUDA environment across deployments
- CUDA 12.1 is compatible with GTX 1050 Ti
- Runtime image is smaller than devel image
- NVIDIA Container Toolkit handles GPU passthrough

**Alternatives Considered:**
- Host installation: Harder to reproduce, dependency conflicts
- CUDA 11.8: Older, but 12.1 provides better performance
- CPU-only Docker: Too slow for production use

**Trade-offs:**
- ✅ Reproducible environment
- ✅ Easy deployment
- ✅ GPU isolation
- ❌ Larger image size (~8GB)
- ❌ Requires NVIDIA Container Toolkit on host

## Risks / Trade-offs

### Risk 1: Model Switching Latency
**Risk:** 5-8 second delay when switching between STT and TTS models may frustrate users

**Mitigation:**
- Document expected latency in API documentation
- Provide optional model preloading configuration (ENABLE_MODEL_PRELOAD)
- Log model switch events for monitoring
- Consider caching strategy for frequent users (future enhancement)

### Risk 2: VRAM Exhaustion
**Risk:** Unexpected VRAM spikes could cause OOM errors

**Mitigation:**
- Implement VRAM monitoring with alerts at 90% usage
- Set conservative batch sizes (max_batch_size=8)
- Graceful error handling with 503 Service Unavailable
- Automatic retry with exponential backoff

### Risk 3: Mirror Source Availability
**Risk:** Chinese mirror sources may be temporarily unavailable

**Mitigation:**
- Configure multiple fallback indexes in pyproject.toml
- Automatic fallback to official sources
- Health check endpoint monitors mirror connectivity
- Document manual mirror switching procedure

### Risk 4: Model Download Failures
**Risk:** Initial model download (~5GB) may fail on slow/unstable connections

**Mitigation:**
- Use HF-Mirror with resume capability
- Implement retry logic with exponential backoff
- Provide pre-downloaded model option via volume mount
- Clear error messages with download progress

### Risk 5: Concurrent Request Handling
**Risk:** Multiple simultaneous requests during model switching could cause race conditions

**Mitigation:**
- Implement request queue with FIFO processing
- Lock mechanism during model switching
- 60-second timeout for queued requests
- Return 503 with Retry-After header when queue is full

### Risk 6: PyTorch Version Compatibility
**Risk:** PyTorch wheels from Tsinghua mirror may lag behind official releases

**Mitigation:**
- Pin specific PyTorch version in dependencies (torch>=2.1.0)
- Test with both mirror and official sources in CI
- Document version compatibility in README
- Provide override mechanism for advanced users

## Migration Plan

### Phase 1: Initial Deployment
1. Build Docker image with all dependencies
2. Download models to persistent volume (first run)
3. Start service with health checks
4. Verify both STT and TTS endpoints
5. Monitor VRAM usage and model switch times

### Phase 2: Configuration Tuning
1. Adjust batch sizes based on actual VRAM usage
2. Configure model preloading if one endpoint is used more frequently
3. Tune timeout values based on observed latencies
4. Set up monitoring and alerting

### Phase 3: Production Hardening
1. Implement rate limiting if needed
2. Add request logging and metrics
3. Set up automated health checks
4. Document operational procedures

### Rollback Strategy
- Keep previous Docker image tagged
- Models are in persistent volume (not affected by rollback)
- Configuration in .env file (easy to revert)
- Zero-downtime rollback: `docker-compose up -d` with old image

### Deployment Checklist
- [ ] NVIDIA drivers installed on host (version >=525)
- [ ] NVIDIA Container Toolkit configured
- [ ] Docker Compose installed
- [ ] 15GB+ free disk space for models
- [ ] GPU accessible via `nvidia-smi`
- [ ] Network access to mirror sources or models pre-downloaded
- [ ] Environment variables configured in .env
- [ ] Firewall rules allow port 8000

## Open Questions

### Q1: Should we support model quantization (INT8)?
**Context:** INT8 quantization could reduce VRAM usage by ~50% but may impact quality

**Options:**
- A: Implement INT8 as optional configuration
- B: Keep FP16 only for quality
- C: Defer until user feedback indicates need

**Recommendation:** Option B initially, revisit based on user feedback

### Q2: Should we implement request caching?
**Context:** Caching could improve performance for repeated requests

**Options:**
- A: Cache STT results by audio file hash
- B: Cache TTS results by (text, voice) tuple
- C: No caching (simpler, stateless)

**Recommendation:** Option C initially, add caching if performance data shows benefit

### Q3: Should we support multiple CUDA versions?
**Context:** Users may have different CUDA versions installed

**Options:**
- A: Provide separate Docker images for CUDA 11.8 and 12.1
- B: Support only CUDA 12.1 (latest stable)
- C: Let users build custom images

**Recommendation:** Option B, document how to build for other CUDA versions

### Q4: Should we implement graceful shutdown?
**Context:** Proper shutdown could prevent model corruption

**Options:**
- A: Implement signal handlers to unload models cleanly
- B: Rely on Docker's default SIGTERM handling
- C: Add drain period for in-flight requests

**Recommendation:** Option A + C for production robustness
