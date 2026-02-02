# OpenTalker

OpenAI 兼容的音频处理 API 服务，支持语音转文字（STT）和文字转语音（TTS），专为 GTX 1050 Ti（4GB 显存）优化。

[![CI](https://github.com/DDKTopLabs/OpenTalker/actions/workflows/ci.yml/badge.svg)](https://github.com/DDKTopLabs/OpenTalker/actions/workflows/ci.yml)
[![Docker Build](https://github.com/DDKTopLabs/OpenTalker/actions/workflows/docker.yml/badge.svg)](https://github.com/DDKTopLabs/OpenTalker/actions/workflows/docker.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.1%2F12.3-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Docker Pulls](https://img.shields.io/docker/pulls/ddktoplabs/opentalker)](https://hub.docker.com/r/ddktoplabs/opentalker)

## ✨ 特性

- 🎯 **完全兼容 OpenAI Audio API** - 无缝替换 OpenAI 的 `/v1/audio/*` 端点
- 🚀 **智能模型管理** - 自动切换 STT/TTS 模型，确保 4GB 显存内运行
- 🎤 **高质量 STT** - 使用 Qwen3-ASR-0.6B，支持多语言和时间戳生成
- 🗣️ **先进 TTS** - 使用 IndexTTS2，支持语音克隆和情感控制
- 🐳 **Docker 部署** - 一键部署，包含 GPU 支持
- 🇨🇳 **国内镜像优化** - 使用清华大学镜像源，下载速度快
- 📊 **性能监控** - GPU 监控、性能统计、健康检查
- 🔧 **灵活配置** - 环境变量配置，支持多种音频格式

## 📋 目录

- [硬件要求](#硬件要求)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
  - [Docker 部署（推荐）](#docker-部署推荐)
  - [本地安装](#本地安装)
- [API 文档](#api-文档)
- [配置参考](#配置参考)
- [镜像源配置](#镜像源配置)
- [性能预期](#性能预期)
- [故障排查](#故障排查)
- [许可证](#许可证)

## 🖥️ 硬件要求

### 最低要求
- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM) 或更高
- **CPU**: 4 核心
- **内存**: 8GB RAM
- **存储**: 20GB 可用空间（用于模型）
- **CUDA**: 12.1 或 12.3

### 推荐配置
- **GPU**: NVIDIA RTX 3060 (12GB VRAM) 或更高
- **CPU**: 8 核心
- **内存**: 16GB RAM
- **存储**: 50GB SSD

### 软件要求
- **操作系统**: Ubuntu 22.04 / 20.04
- **Docker**: 20.10+ (Docker 部署)
- **NVIDIA Driver**: 525+ (支持 CUDA 12.x)
- **NVIDIA Container Toolkit**: 最新版本

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/DDKTopLabs/OpenTalker.git
cd OpenTalker

# 2. 下载模型（使用 HF-Mirror，国内速度快）
./scripts/download_models.sh

# 3. 启动服务
docker-compose up -d

# 4. 检查状态
curl http://localhost:8000/health

# 5. 测试 STT
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@audio.mp3" \
  -F "model=qwen3-asr-0.6b"

# 6. 测试 TTS
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "indextts-2",
    "input": "你好，世界！",
    "voice": "<base64_encoded_reference_audio>"
  }' \
  --output speech.wav
```

### 使用 Python 客户端

```python
import openai

# 配置 API 端点
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "dummy"  # 不需要真实 API key

# STT - 语音转文字
with open("audio.mp3", "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        model="qwen3-asr-0.6b",
        file=audio_file,
        response_format="json"
    )
    print(transcript.text)

# TTS - 文字转语音
import base64

# 读取参考音频
with open("reference.wav", "rb") as f:
    voice_data = base64.b64encode(f.read()).decode()

response = openai.Audio.create_speech(
    model="indextts-2",
    input="你好，世界！",
    voice=voice_data
)

# 保存音频
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## 📦 安装指南

### Docker 部署（推荐）

#### 1. 安装 NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

#### 2. 验证 GPU 支持

```bash
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi
```

#### 3. 下载模型

```bash
# 使用 Bash 脚本（推荐）
./scripts/download_models.sh

# 或使用 Python 脚本
python scripts/init_models.py --include-aligner
```

#### 4. 配置环境变量（可选）

```bash
cp .env.example .env
# 编辑 .env 文件修改配置
```

#### 5. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 本地安装

#### 1. 安装系统依赖

```bash
# Ubuntu 22.04
sudo apt-get update
sudo apt-get install -y \
  python3.11 \
  python3.11-dev \
  ffmpeg \
  libsndfile1 \
  libsndfile1-dev \
  build-essential
```

#### 2. 安装 uv 包管理器

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

#### 3. 安装 Python 依赖

```bash
# 使用 uv（推荐，自动使用清华镜像）
uv pip install -e .

# 或使用 pip
pip install -e .
```

#### 4. 下载模型

```bash
./scripts/download_models.sh
```

#### 5. 启动服务

```bash
# 开发模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## 📚 API 文档

### 端点概览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/v1/audio/transcriptions` | POST | 语音转文字（STT） |
| `/v1/audio/speech` | POST | 文字转语音（TTS） |
| `/v1/models` | GET | 列出可用模型 |
| `/health` | GET | 健康检查 |
| `/metrics` | GET | 性能指标 |

### STT - 语音转文字

**端点**: `POST /v1/audio/transcriptions`

**请求参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `file` | file | 是 | 音频文件（MP3, WAV, FLAC, M4A, OGG, WEBM） |
| `model` | string | 否 | 模型名称（默认: `qwen3-asr-0.6b`） |
| `language` | string | 否 | 语言代码（ISO-639-1，如 `zh`, `en`） |
| `response_format` | string | 否 | 响应格式（`json`, `text`, `srt`, `vtt`, `verbose_json`） |
| `temperature` | float | 否 | 采样温度（0.0-1.0，默认: 0.0） |
| `timestamp_granularities` | string | 否 | 时间戳粒度（`word`, `segment`，逗号分隔） |

**响应示例**:

```json
{
  "text": "你好，世界！"
}
```

**Verbose JSON 响应**:

```json
{
  "task": "transcribe",
  "language": "zh",
  "duration": 2.5,
  "text": "你好，世界！",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 2.5,
      "text": "你好，世界！"
    }
  ],
  "words": [
    {"word": "你好", "start": 0.0, "end": 1.2},
    {"word": "世界", "start": 1.5, "end": 2.5}
  ]
}
```

**cURL 示例**:

```bash
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@audio.mp3" \
  -F "model=qwen3-asr-0.6b" \
  -F "response_format=json" \
  -F "language=zh"
```

### TTS - 文字转语音

**端点**: `POST /v1/audio/speech`

**请求参数**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `model` | string | 否 | 模型名称（默认: `indextts-2`） |
| `input` | string | 是 | 要合成的文本（1-4096 字符） |
| `voice` | string | 是 | Base64 编码的参考音频（用于语音克隆） |
| `response_format` | string | 否 | 音频格式（`wav`, `mp3`, `flac`, `opus`） |
| `speed` | float | 否 | 语速（0.25-4.0，默认: 1.0） |
| `emotion` | object | 否 | 情感控制配置 |

**情感控制参数**:

```json
{
  "mode": "auto",  // auto, audio, vector, text
  "alpha": 1.0,    // 情感强度 (0.0-1.0)
  "audio": "<base64_audio>",  // 情感参考音频
  "vector": [0.1, 0.2, ...],  // 情感向量
  "text": "开心"               // 情感文本描述
}
```

**请求示例**:

```json
{
  "model": "indextts-2",
  "input": "你好，世界！这是一个测试。",
  "voice": "UklGRiQAAABXQVZFZm10...",
  "response_format": "wav",
  "speed": 1.0,
  "emotion": {
    "mode": "auto",
    "alpha": 1.0
  }
}
```

**cURL 示例**:

```bash
# 准备参考音频
VOICE_BASE64=$(base64 -w 0 reference.wav)

# 发送请求
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"indextts-2\",
    \"input\": \"你好，世界！\",
    \"voice\": \"$VOICE_BASE64\",
    \"response_format\": \"wav\"
  }" \
  --output output.wav
```

### 健康检查

**端点**: `GET /health`

**响应示例**:

```json
{
  "status": "healthy",
  "gpu": {
    "device_name": "NVIDIA GeForce GTX 1050 Ti",
    "total_memory_mb": 4096.0,
    "used_memory_mb": 1234.5,
    "free_memory_mb": 2861.5,
    "utilization_percent": 30.1
  },
  "model": {
    "model_type": "stt",
    "status": "loaded",
    "model_name": "Qwen/Qwen3-ASR-0.6B"
  }
}
```

### 列出模型

**端点**: `GET /v1/models`

**响应示例**:

```json
{
  "object": "list",
  "data": [
    {
      "id": "qwen3-asr-0.6b",
      "object": "model",
      "created": 1704067200,
      "owned_by": "qwen"
    },
    {
      "id": "indextts-2",
      "object": "model",
      "created": 1704067200,
      "owned_by": "indextts"
    }
  ]
}
```

## ⚙️ 配置参考

### 环境变量

所有配置通过环境变量设置，可以在 `.env` 文件或 `docker-compose.yml` 中配置。

#### HuggingFace 镜像

```bash
# HuggingFace 镜像端点（国内使用 HF-Mirror）
HF_ENDPOINT=https://hf-mirror.com

# 模型缓存目录
HUGGINGFACE_HUB_CACHE=/models/.cache/huggingface
```

#### STT 配置（Qwen3-ASR）

```bash
# 模型标识
QWEN_ASR_MODEL=Qwen/Qwen3-ASR-0.6B

# 后端（transformers 或 onnx）
QWEN_ASR_BACKEND=transformers

# 数据类型（float16 或 float32）
QWEN_ASR_DTYPE=float16

# 设备（cuda:0 或 cpu）
QWEN_ASR_DEVICE=cuda:0

# 启用强制对齐器（auto, true, false）
QWEN_ASR_ENABLE_ALIGNER=auto

# 最大批处理大小
QWEN_ASR_MAX_BATCH_SIZE=8
```

#### TTS 配置（IndexTTS2）

```bash
# 模型目录
INDEXTTS_MODEL_DIR=/models/indextts

# 使用 FP16 精度
INDEXTTS_USE_FP16=true

# 使用 CUDA 内核优化（需要编译）
INDEXTTS_USE_CUDA_KERNEL=false

# 使用 DeepSpeed
INDEXTTS_USE_DEEPSPEED=false
```

#### 服务配置

```bash
# API 主机
API_HOST=0.0.0.0

# API 端口
API_PORT=8000

# 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
LOG_LEVEL=INFO

# 最大上传文件大小（字节）
MAX_UPLOAD_SIZE=52428800  # 50MB
```

#### GPU 配置

```bash
# CUDA 可见设备
CUDA_VISIBLE_DEVICES=0
```

#### 模型管理

```bash
# 模型切换超时（秒）
MODEL_SWITCH_TIMEOUT=30

# 启用模型预加载
ENABLE_MODEL_PRELOAD=false

# 默认预加载模型（none, stt, tts）
DEFAULT_PRELOAD_MODEL=none
```

## 🔧 镜像源配置

本项目针对国内网络环境优化，使用清华大学镜像源。

### PyPI 镜像（Python 包）

配置在 `pyproject.toml` 中：

```toml
[[tool.uv.index]]
name = "tsinghua-pypi"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

### PyTorch 镜像（CUDA 12.1）

```toml
[tool.uv.sources]
torch = { index = "tsinghua-pytorch" }
torchaudio = { index = "tsinghua-pytorch" }

[[tool.uv.index]]
name = "tsinghua-pytorch"
url = "https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cu121"
explicit = true
```

### HuggingFace 镜像（模型下载）

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Ubuntu APT 镜像

Dockerfile 中自动配置：

```dockerfile
RUN sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list
```

### CUDA 版本切换

如需切换 CUDA 版本，修改 `pyproject.toml`：

```toml
# CUDA 12.1 (默认)
[[tool.uv.index]]
name = "tsinghua-pytorch"
url = "https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cu121"

# CUDA 11.8
[[tool.uv.index]]
name = "tsinghua-pytorch"
url = "https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cu118"

# CPU only
[[tool.uv.index]]
name = "tsinghua-pytorch"
url = "https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cpu"
```

同时更新 Dockerfile 基础镜像：

```dockerfile
# CUDA 12.1
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# CUDA 11.8
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
```

## 📊 性能预期

### GTX 1050 Ti (4GB VRAM)

| 操作 | 延迟 | 吞吐量 | 显存占用 |
|------|------|--------|----------|
| STT (Qwen3-ASR-0.6B) | 0.5-2s | ~30s 音频/s | ~2.5GB |
| TTS (IndexTTS2) | 1-3s | ~10 字符/s | ~3.0GB |
| 模型切换 | 5-10s | - | - |

### RTX 3060 (12GB VRAM)

| 操作 | 延迟 | 吞吐量 | 显存占用 |
|------|------|--------|----------|
| STT (Qwen3-ASR-0.6B) | 0.2-1s | ~60s 音频/s | ~2.5GB |
| TTS (IndexTTS2) | 0.5-1.5s | ~20 字符/s | ~3.0GB |
| 模型切换 | 3-5s | - | - |

### 注意事项

- **模型切换**: 由于 4GB 显存限制，STT 和 TTS 不能同时加载，切换需要 5-10 秒
- **批处理**: 不支持批处理，一次只能处理一个请求
- **并发**: 请求会排队处理，不支持真正的并发
- **长音频**: 超过 30 秒的音频可能需要更长处理时间
- **长文本**: TTS 会自动分段处理超过 1000 字符的文本

## 🔍 故障排查

### 1. GPU 不可用

**症状**: `CUDA not available` 或 `No CUDA device`

**解决方案**:

```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi

# 重新安装 NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. 模型下载失败

**症状**: `Connection timeout` 或 `Failed to download`

**解决方案**:

```bash
# 使用 HF-Mirror（国内）
export HF_ENDPOINT=https://hf-mirror.com

# 重新下载
./scripts/download_models.sh

# 或手动下载
huggingface-cli download Qwen/Qwen3-ASR-0.6B --local-dir ./models/qwen3-asr
```

### 3. 显存不足

**症状**: `CUDA out of memory`

**解决方案**:

```bash
# 检查显存使用
nvidia-smi

# 确保只有一个模型加载
# 检查 /health 端点查看当前模型状态

# 降低批处理大小
export QWEN_ASR_MAX_BATCH_SIZE=4

# 使用 float32 代替 float16（需要更多显存）
export QWEN_ASR_DTYPE=float32
```

### 4. 模型加载超时

**症状**: `Model loading timeout`

**解决方案**:

```bash
# 增加超时时间
export MODEL_SWITCH_TIMEOUT=60

# 预加载模型（启动时加载）
export ENABLE_MODEL_PRELOAD=true
export DEFAULT_PRELOAD_MODEL=stt  # 或 tts
```

### 5. 音频格式不支持

**症状**: `Invalid audio file` 或 `Unsupported format`

**解决方案**:

```bash
# 安装 ffmpeg
sudo apt-get install -y ffmpeg

# 转换音频格式
ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav

# 支持的格式: MP3, WAV, FLAC, M4A, OGG, WEBM
```

### 6. Docker 容器无法启动

**症状**: 容器启动后立即退出

**解决方案**:

```bash
# 查看日志
docker-compose logs

# 检查配置
docker-compose config

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 7. API 响应慢

**症状**: 请求超时或响应时间长

**解决方案**:

- 首次请求会触发模型加载（5-10 秒）
- 后续请求应该更快
- 检查 GPU 利用率: `nvidia-smi`
- 检查性能指标: `curl http://localhost:8000/metrics`

### 8. 依赖安装失败

**症状**: `pip install` 失败或超时

**解决方案**:

```bash
# 使用 uv（更快，自动使用镜像）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -e .

# 或手动配置 pip 镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e .
```

## 📝 使用示例

### Python 完整示例

```python
import openai
import base64
from pathlib import Path

# 配置
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "dummy"

def transcribe_audio(audio_path: str) -> str:
    """语音转文字"""
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="qwen3-asr-0.6b",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"]
        )
    return transcript

def synthesize_speech(text: str, reference_audio: str, output_path: str):
    """文字转语音"""
    # 读取参考音频
    with open(reference_audio, "rb") as f:
        voice_data = base64.b64encode(f.read()).decode()
    
    # 合成语音
    response = openai.Audio.create_speech(
        model="indextts-2",
        input=text,
        voice=voice_data,
        response_format="wav",
        speed=1.0
    )
    
    # 保存
    with open(output_path, "wb") as f:
        f.write(response.content)

# 使用
if __name__ == "__main__":
    # STT
    result = transcribe_audio("input.mp3")
    print(f"Transcription: {result.text}")
    print(f"Duration: {result.duration}s")
    
    # TTS
    synthesize_speech(
        text="你好，世界！这是一个测试。",
        reference_audio="reference.wav",
        output_path="output.wav"
    )
    print("Speech synthesized!")
```

### cURL 完整示例

```bash
#!/bin/bash

API_BASE="http://localhost:8000"

# 1. 健康检查
echo "Checking health..."
curl -s "$API_BASE/health" | jq .

# 2. 列出模型
echo -e "\nListing models..."
curl -s "$API_BASE/v1/models" | jq .

# 3. STT - 语音转文字
echo -e "\nTranscribing audio..."
curl -X POST "$API_BASE/v1/audio/transcriptions" \
  -F "file=@audio.mp3" \
  -F "model=qwen3-asr-0.6b" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities=word,segment" \
  | jq .

# 4. TTS - 文字转语音
echo -e "\nSynthesizing speech..."
VOICE_BASE64=$(base64 -w 0 reference.wav)

curl -X POST "$API_BASE/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"indextts-2\",
    \"input\": \"你好，世界！\",
    \"voice\": \"$VOICE_BASE64\",
    \"response_format\": \"wav\",
    \"speed\": 1.0
  }" \
  --output output.wav

echo "Done!"
```

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Qwen3-ASR](https://github.com/QwenLM/Qwen-Audio) - 高质量语音识别模型
- [IndexTTS2](https://github.com/IndexTeam/IndexTTS) - 先进的语音合成模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [uv](https://github.com/astral-sh/uv) - 快速 Python 包管理器
- 清华大学开源软件镜像站 - 提供镜像服务

## 📧 联系方式

- 项目主页: https://github.com/DDKTopLabs/OpenTalker
- 问题反馈: https://github.com/DDKTopLabs/OpenTalker/issues

## 🗺️ 路线图

- [ ] 支持流式 TTS 输出
- [ ] 支持批处理 STT
- [ ] 添加更多 TTS 模型
- [ ] 支持更多语言
- [ ] Web UI 界面
- [ ] 性能优化
- [ ] 完整的测试套件

---

**注意**: 本项目仅供学习和研究使用。请遵守相关模型的使用条款和许可证。
