## Why

中国大陆用户需要一个本地化的、兼容 OpenAI API 的音频处理服务，支持语音识别（STT）和语音合成（TTS）功能。现有的 OpenAI API 在中国访问受限且成本高昂，而开源模型（Qwen3-ASR 和 IndexTTS2）提供了高质量的中文支持。此项目针对 GTX 1050 Ti (4GB 显存) 等入门级 GPU 进行优化，使用清华大学镜像源加速部署，为个人开发者和小团队提供可负担的解决方案。

## What Changes

- 创建基于 FastAPI 的 REST API 服务，完全兼容 OpenAI Audio API 格式
- 集成 Qwen3-ASR-0.6B 模型提供语音转文字功能（支持 52 种语言）
- 集成 IndexTTS2 模型提供文字转语音功能（支持情感控制和零样本语音克隆）
- 实现智能模型管理器，在 4GB 显存限制下按需加载/卸载模型
- 使用 uv 包管理器和清华大学镜像源（PyPI、PyTorch、HuggingFace）加速部署
- 提供 Docker 镜像支持 NVIDIA GPU 加速
- 支持词级时间戳（通过 Qwen3-ForcedAligner，可选）

## Capabilities

### New Capabilities

- `speech-to-text-api`: OpenAI 兼容的 `/v1/audio/transcriptions` 端点，支持多种音频格式输入，返回转录文本、语言识别和可选的时间戳信息
- `text-to-speech-api`: OpenAI 兼容的 `/v1/audio/speech` 端点，支持零样本语音克隆、情感控制（4 种模式）和高质量音频输出
- `model-management`: 智能模型加载/卸载系统，在 4GB 显存约束下自动管理 Qwen3-ASR 和 IndexTTS2 模型的生命周期
- `gpu-monitoring`: GPU 显存使用监控和统计，提供实时显存占用信息和模型切换性能指标
- `mirror-configuration`: 集成清华大学镜像源配置（PyPI、PyTorch、HuggingFace），使用 uv 的 `tool.uv.sources` 和 `explicit` 索引机制

### Modified Capabilities

无现有能力需要修改。

## Impact

**新增组件**：
- `app/` - FastAPI 应用代码
  - `main.py` - 应用入口
  - `core/model_manager.py` - 模型管理器
  - `services/stt_service.py` - STT 服务封装
  - `services/tts_service.py` - TTS 服务封装
  - `routers/audio.py` - API 路由
- `pyproject.toml` - uv 项目配置，包含所有镜像源配置
- `Dockerfile` - CUDA 12.1 容器镜像
- `docker-compose.yml` - 服务编排配置

**依赖项**：
- Python 3.10-3.12
- PyTorch 2.1.0+ (CUDA 12.1)
- qwen-asr 0.1.0+ (Transformers 后端)
- FastAPI 0.109.0+
- uv 包管理器

**硬件要求**：
- NVIDIA GPU with 4GB+ VRAM (GTX 1050 Ti 或更高)
- CUDA Compute Capability 6.1+ (GTX 1050 Ti 支持)
- 15GB+ 磁盘空间（模型缓存）

**网络要求**：
- 首次启动需要下载模型（约 5GB）
- 使用清华镜像源加速中国大陆访问

**性能特征**：
- STT 处理速度：10 秒音频约 2-3 秒（GTX 1050 Ti）
- TTS 处理速度：短句约 1-2 秒
- 模型切换时间：5-8 秒（一次性开销）
- 显存峰值：2.5-2.8GB（单模型）
