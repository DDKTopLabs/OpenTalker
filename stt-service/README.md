# OpenTalker STT Service

Qwen3-ASR 语音转文字服务

## 特性

- ✅ 独立的 STT 服务
- ✅ 使用 qwen-asr 0.0.6
- ✅ transformers >= 4.57.0
- ✅ 支持多语言识别
- ✅ 支持时间戳生成

## 快速开始

```bash
# 安装依赖
cd stt-service
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install -e .

# 启动服务
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## API 端点

### POST /transcribe

转录音频文件

**请求参数：**
- `file`: 音频文件（必需）
- `language`: 语言代码（可选，如 'Chinese', 'English'）
- `response_format`: 响应格式（json, text, srt, vtt, verbose_json）
- `timestamp_granularities`: 时间戳粒度（word, segment）
- `temperature`: 采样温度（0.0-1.0）

**示例：**

```bash
curl -X POST http://localhost:8001/transcribe \
  -F "file=@audio.wav" \
  -F "language=Chinese" \
  -F "response_format=json"
```

### GET /health

健康检查

```bash
curl http://localhost:8001/health
```

## 环境变量

创建 `.env` 文件：

```bash
# Service
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
LOG_LEVEL=INFO

# Model
QWEN_ASR_MODEL=./models/qwen3-asr
QWEN_ASR_DEVICE=cpu
QWEN_ASR_MAX_BATCH_SIZE=8

# Upload
MAX_UPLOAD_SIZE=52428800

# HuggingFace
HF_ENDPOINT=https://hf-mirror.com
```

## 依赖版本

- qwen-asr: 0.0.6
- transformers: >= 4.57.0, < 5.0.0
- torch: >= 2.1.0
- numpy: < 2.0.0
