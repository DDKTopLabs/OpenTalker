# OpenTalker Workspace

OpenAI 兼容的音频处理 API 服务 - 微服务架构

## 🎯 架构设计

本项目采用 **uv workspace** 微服务架构，将 STT 和 TTS 分离为独立服务，完美解决依赖冲突问题。

```
┌─────────────────────────────────────────────────────────┐
│                    Client (OpenAI API)                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Gateway (Port 8000)                         │
│  - OpenAI 兼容接口                                        │
│  - 请求路由                                               │
│  - 无模型依赖                                             │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
       ┌───────▼────────┐    ┌───────▼────────┐
       │  STT Service   │    │  TTS Service   │
       │  (Port 8001)   │    │  (Port 8002)   │
       │                │    │                │
       │  Qwen3-ASR     │    │  IndexTTS2     │
       │  transformers  │    │  transformers  │
       │  >= 4.57.0     │    │  < 4.57.0      │
       └────────────────┘    └────────────────┘
```

## ✨ 核心优势

### 1. 依赖隔离
- ✅ **STT 服务**: 使用 `transformers >= 4.57.0`（qwen-asr 要求）
- ✅ **TTS 服务**: 使用 `transformers < 4.57.0`（indextts 要求）
- ✅ **Gateway**: 无模型依赖，轻量级

### 2. 独立扩展
- 🚀 每个服务可独立部署、扩展
- 🔄 支持独立更新和重启
- 📊 独立的资源管理和监控

### 3. 开发友好
- 🛠️ 使用 uv workspace 统一管理
- 📦 每个服务有独立的 `pyproject.toml`
- 🧪 独立的测试和开发环境

## 📦 项目结构

```
opentalker/
├── pyproject.toml              # Workspace 配置
├── docker-compose.workspace.yml # 多服务编排
├── README.md                   # 本文件
│
├── gateway/                    # API 网关
│   ├── pyproject.toml         # 依赖: fastapi, httpx
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── routers/
│   │       ├── audio.py       # 代理到 STT/TTS
│   │       └── health.py
│   └── README.md
│
├── stt-service/                # STT 独立服务
│   ├── pyproject.toml         # 依赖: qwen-asr, transformers>=4.57
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── service.py         # Qwen3-ASR 封装
│   └── README.md
│
└── tts-service/                # TTS 独立服务
    ├── pyproject.toml         # 依赖: indextts, transformers<4.57
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   └── service.py         # IndexTTS2 封装
    └── README.md
```

## 🚀 快速开始

### 方式 1: 使用 uv workspace（推荐）

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone https://github.com/DDKTopLabs/OpenTalker.git
cd OpenTalker

# 3. 安装所有服务的依赖
uv sync

# 4. 启动服务（三个终端）

# 终端 1: 启动 STT 服务
cd stt-service
uv run python -m app.main

# 终端 2: 启动 TTS 服务
cd tts-service
uv run python -m app.main

# 终端 3: 启动 Gateway
cd gateway
uv run python -m app.main
```

### 方式 2: 使用 Docker Compose

```bash
# 1. 构建并启动所有服务
docker-compose -f docker-compose.workspace.yml up -d

# 2. 查看日志
docker-compose -f docker-compose.workspace.yml logs -f

# 3. 停止服务
docker-compose -f docker-compose.workspace.yml down
```

### 方式 3: 独立启动单个服务

```bash
# 只启动 STT 服务
cd stt-service
uv venv
source .venv/bin/activate
uv pip install -e .
python -m app.main

# 只启动 TTS 服务
cd tts-service
uv venv
source .venv/bin/activate
uv pip install -e .
python -m app.main
```

## 📚 API 使用

### 健康检查

```bash
# Gateway 健康检查（会检查所有后端服务）
curl http://localhost:8000/health

# STT 服务健康检查
curl http://localhost:8001/health

# TTS 服务健康检查
curl http://localhost:8002/health
```

### STT - 语音转文字

```bash
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=qwen3-asr" \
  -F "language=Chinese"
```

### TTS - 文字转语音

```bash
VOICE_BASE64=$(base64 -i reference.wav)

curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"indextts-2\",
    \"input\": \"你好世界\",
    \"voice\": \"$VOICE_BASE64\"
  }" \
  --output speech.wav
```

## ⚙️ 配置

每个服务都有独立的环境变量配置：

### Gateway (.env)
```bash
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
STT_SERVICE_URL=http://localhost:8001
TTS_SERVICE_URL=http://localhost:8002
STT_TIMEOUT=120
TTS_TIMEOUT=180
```

### STT Service (.env)
```bash
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
QWEN_ASR_MODEL=./models/qwen3-asr
QWEN_ASR_DEVICE=cpu
HF_ENDPOINT=https://hf-mirror.com
```

### TTS Service (.env)
```bash
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8002
INDEXTTS_MODEL_DIR=./models/indextts
INDEXTTS_DEVICE=cpu
HF_ENDPOINT=https://hf-mirror.com
```

## 🔧 开发指南

### 添加新功能

```bash
# 1. 在对应服务目录下开发
cd stt-service  # 或 tts-service, gateway

# 2. 安装开发依赖
uv pip install -e ".[dev]"

# 3. 运行测试
uv run pytest

# 4. 代码格式化
uv run black app/
uv run ruff check app/
```

### 依赖管理

```bash
# 为特定服务添加依赖
cd stt-service
uv add <package-name>

# 更新依赖
uv sync

# 查看依赖树
uv tree
```

## 📊 性能对比

| 架构 | 优点 | 缺点 |
|------|------|------|
| **单体应用** | 部署简单 | ❌ 依赖冲突无法解决 |
| **Workspace** | ✅ 依赖隔离<br>✅ 独立扩展<br>✅ 易于维护 | 需要多个进程 |

## 🐛 故障排查

### 问题 1: Gateway 无法连接到后端服务

```bash
# 检查服务是否运行
curl http://localhost:8001/health  # STT
curl http://localhost:8002/health  # TTS

# 检查端口占用
lsof -i :8001
lsof -i :8002
```

### 问题 2: 依赖安装失败

```bash
# 清理并重新安装
cd stt-service  # 或其他服务
rm -rf .venv
uv venv
uv pip install -e .
```

### 问题 3: 模型加载失败

```bash
# 检查模型文件
ls -lh models/qwen3-asr/
ls -lh models/indextts/

# 下载模型
./scripts/download_models.sh
```

## 📝 版本历史

### v0.2.0 (2026-02-04)
- ✅ 重构为 workspace 微服务架构
- ✅ 解决 transformers 版本冲突
- ✅ 独立的 STT/TTS 服务
- ✅ API Gateway 统一入口

### v0.1.0 (2026-02-03)
- ✅ 初始版本（单体应用）
- ✅ Qwen3-ASR + IndexTTS2
- ❌ 存在依赖冲突问题

## 📄 许可证

Apache License 2.0

## 🙏 致谢

- [Qwen3-ASR](https://github.com/QwenLM/Qwen-Audio)
- [IndexTTS2](https://github.com/IndexTeam/IndexTTS)
- [FastAPI](https://fastapi.tiangolo.com/)
- [uv](https://github.com/astral-sh/uv)
