# OpenTalker API Gateway

OpenAI 兼容的音频 API 网关

## 特性

- ✅ OpenAI 兼容的 API 接口
- ✅ 代理请求到 STT/TTS 服务
- ✅ 轻量级，无模型依赖
- ✅ 支持服务健康检查
- ✅ 自动负载均衡（未来）

## 快速开始

```bash
# 安装依赖
cd gateway
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install -e .

# 启动网关
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 端点

### POST /v1/audio/transcriptions

语音转文字（代理到 STT 服务）

```bash
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=qwen3-asr"
```

### POST /v1/audio/speech

文字转语音（代理到 TTS 服务）

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "indextts-2",
    "input": "你好世界",
    "voice": "<base64_audio>"
  }' \
  --output speech.wav
```

### GET /health

健康检查

```bash
curl http://localhost:8000/health
```

### GET /v1/models

列出可用模型

```bash
curl http://localhost:8000/v1/models
```

## 环境变量

创建 `.env` 文件：

```bash
# Gateway
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
LOG_LEVEL=INFO

# Backend Services
STT_SERVICE_URL=http://localhost:8001
TTS_SERVICE_URL=http://localhost:8002

# Timeouts
STT_TIMEOUT=120
TTS_TIMEOUT=180
```

## 架构

```
Client → Gateway (8000) → STT Service (8001)
                        → TTS Service (8002)
```

网关负责：
- 接收 OpenAI 兼容的 API 请求
- 路由到对应的后端服务
- 返回统一格式的响应
- 健康检查和监控
