# OpenTalker TTS Service

Qwen3-TTS 文字转语音服务

## 特性

- ✅ 独立的 TTS 服务
- ✅ 使用 Qwen3-TTS (0.6B/1.7B)
- ✅ 支持 10 种语言
- ✅ 支持多种音色
- ✅ 支持语速控制

## 快速开始

```bash
# 安装依赖
cd tts-service
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install fastapi uvicorn python-multipart pydantic pydantic-settings qwen-tts torch torchaudio "numpy<2.0.0" soundfile

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
  "speaker": "female_calm",
  "language": "zh",
  "response_format": "wav",
  "speed": 1.0
}
```

**示例：**

```bash
curl -X POST http://localhost:8002/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你好世界",
    "speaker": "female_calm",
    "language": "zh"
  }' \
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
QWEN_TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
QWEN_TTS_DEVICE=cpu
QWEN_TTS_SPEAKER=female_calm

# HuggingFace
HF_ENDPOINT=https://hf-mirror.com
```

## 支持的音色

- female_calm - 女声平静
- male_energetic - 男声活力
- 等等（通过 API 查询完整列表）

## 支持的语言

- zh - 中文
- en - 英语
- ja - 日语
- ko - 韩语
- de - 德语
- fr - 法语
- ru - 俄语
- pt - 葡萄牙语
- es - 西班牙语
- it - 意大利语

## 依赖版本

- qwen-tts: >= 0.1.0
- torch: >= 2.1.0
- numpy: < 2.0.0
