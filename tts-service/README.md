# OpenTalker TTS Service

IndexTTS2 文字转语音服务

## 特性

- ✅ 独立的 TTS 服务
- ✅ 使用 indextts 2.0.0
- ✅ transformers 4.46.x - 4.56.x
- ✅ 支持语音克隆
- ✅ 支持情感控制

## 快速开始

```bash
# 安装依赖
cd tts-service
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install -e .

# 启动服务
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## API 端点

### POST /synthesize

合成语音

**请求体：**

```json
{
  "input": "要合成的文本",
  "voice": "<base64_encoded_reference_audio>",
  "response_format": "wav",
  "speed": 1.0,
  "emotion": {
    "mode": "auto",
    "alpha": 1.0
  }
}
```

**示例：**

```bash
VOICE_BASE64=$(base64 -i reference.wav)

curl -X POST http://localhost:8002/synthesize \
  -H "Content-Type: application/json" \
  -d "{
    \"input\": \"你好世界\",
    \"voice\": \"$VOICE_BASE64\",
    \"response_format\": \"wav\"
  }" \
  --output output.wav
```

### GET /health

健康检查

```bash
curl http://localhost:8002/health
```

## 环境变量

创建 `.env` 文件：

```bash
# Service
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8002
LOG_LEVEL=INFO

# Model
INDEXTTS_MODEL_DIR=./models/indextts
INDEXTTS_DEVICE=cpu
INDEXTTS_USE_FP16=true

# HuggingFace
HF_ENDPOINT=https://hf-mirror.com
```

## 依赖版本

- indextts: >= 2.0.0
- transformers: >= 4.46.0, < 4.57.0
- torch: >= 2.1.0
- numpy: < 2.0.0
