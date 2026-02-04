# OpenTalker Docker 部署指南

## 📋 前置要求

### 硬件要求
- **GPU**: NVIDIA GPU with CUDA support (推荐RTX 2080 Ti或更高)
- **显存**: 至少8GB (推荐22GB+)
- **内存**: 至少16GB
- **磁盘**: 至少20GB可用空间

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **NVIDIA Container Toolkit**: 用于GPU支持

## 🚀 快速开始

### 1. 安装NVIDIA Container Toolkit

**Ubuntu/Debian:**
```bash
# 添加仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 重启Docker
sudo systemctl restart docker
```

**验证安装:**
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 2. 编译Docker镜像

```bash
# 克隆仓库
git clone https://github.com/DDKTopLabs/OpenTalker.git
cd OpenTalker

# 编译所有镜像
./build_docker.sh
```

编译时间约15-30分钟，取决于网络速度。

### 3. 启动服务

```bash
# 使用docker-compose启动
docker-compose -f docker-compose.workspace.yml up -d

# 查看日志
docker-compose -f docker-compose.workspace.yml logs -f

# 等待服务启动（约1-2分钟）
```

### 4. 验证服务

```bash
# 检查所有服务状态
curl http://localhost:8000/health | jq

# 检查STT服务
curl http://localhost:8001/health | jq

# 检查TTS服务
curl http://localhost:8002/health | jq
```

## 📦 镜像说明

### Gateway镜像
- **基础镜像**: python:3.11-slim
- **大小**: ~200MB
- **用途**: API网关，路由请求
- **GPU**: 不需要

### STT Service镜像
- **基础镜像**: nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
- **大小**: ~8GB
- **用途**: 语音识别 (Qwen3-ASR-0.6B)
- **GPU**: 需要 (~3GB显存)

### TTS Service镜像
- **基础镜像**: nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
- **大小**: ~8GB
- **用途**: 语音合成 (Qwen3-TTS-12Hz-0.6B)
- **GPU**: 需要 (~3GB显存)

## 🔧 配置说明

### 环境变量

**Gateway:**
```yaml
GATEWAY_HOST: 0.0.0.0
GATEWAY_PORT: 8000
STT_SERVICE_URL: http://stt-service:8001
TTS_SERVICE_URL: http://tts-service:8002
STT_TIMEOUT: 120
TTS_TIMEOUT: 180
LOG_LEVEL: INFO
```

**STT Service:**
```yaml
SERVICE_HOST: 0.0.0.0
SERVICE_PORT: 8001
QWEN_ASR_MODEL: Qwen/Qwen3-ASR-0.6B
QWEN_ASR_DEVICE: cuda:0
QWEN_ASR_MAX_BATCH_SIZE: 8
MAX_UPLOAD_SIZE: 52428800
HF_ENDPOINT: https://hf-mirror.com
LOG_LEVEL: INFO
```

**TTS Service:**
```yaml
SERVICE_HOST: 0.0.0.0
SERVICE_PORT: 8002
QWEN_TTS_MODEL: Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
QWEN_TTS_DEVICE: cuda:0
HF_ENDPOINT: https://hf-mirror.com
LOG_LEVEL: INFO
```

### 端口映射

- **8000**: Gateway (OpenAI兼容API)
- **8001**: STT Service (语音识别)
- **8002**: TTS Service (语音合成)

### 数据卷

```yaml
volumes:
  - ./models:/models              # 模型缓存目录
  - ./stt-service/tmp:/app/tmp   # STT临时文件
```

## 🧪 测试API

### STT (语音识别)

```bash
# 通过Gateway
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F 'file=@audio.wav' \
  -F 'model=qwen3-asr' \
  -F 'language=Chinese'

# 直接调用STT服务
curl -X POST http://localhost:8001/transcribe \
  -F 'file=@audio.wav' \
  -F 'language=Chinese'
```

### TTS (语音合成)

```bash
# 直接调用TTS服务
curl -X POST http://localhost:8002/synthesize \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "你好世界",
    "speaker": "vivian",
    "language": "Chinese"
  }' \
  -o output.wav
```

## 📊 监控和管理

### 查看容器状态
```bash
docker-compose -f docker-compose.workspace.yml ps
```

### 查看资源使用
```bash
docker stats
```

### 查看GPU使用
```bash
docker exec opentalker-stt nvidia-smi
```

### 查看日志
```bash
# 所有服务
docker-compose -f docker-compose.workspace.yml logs -f

# 特定服务
docker-compose -f docker-compose.workspace.yml logs -f gateway
docker-compose -f docker-compose.workspace.yml logs -f stt-service
docker-compose -f docker-compose.workspace.yml logs -f tts-service
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f docker-compose.workspace.yml restart

# 重启特定服务
docker-compose -f docker-compose.workspace.yml restart stt-service
```

### 停止服务
```bash
docker-compose -f docker-compose.workspace.yml down
```

### 清理
```bash
# 停止并删除容器
docker-compose -f docker-compose.workspace.yml down

# 删除镜像
docker rmi opentalker/gateway:latest
docker rmi opentalker/stt-service:latest
docker rmi opentalker/tts-service:latest

# 清理未使用的镜像和容器
docker system prune -a
```

## 🐛 故障排查

### 问题1: GPU不可用

**症状**: 服务启动但无法使用GPU

**解决方案**:
```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查Docker GPU支持
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# 重启Docker
sudo systemctl restart docker
```

### 问题2: 模型下载失败

**症状**: 服务启动时卡在模型下载

**解决方案**:
```bash
# 使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com

# 或预先下载模型到./models目录
```

### 问题3: 内存不足

**症状**: 容器OOM (Out of Memory)

**解决方案**:
```yaml
# 在docker-compose.yml中限制内存
services:
  stt-service:
    mem_limit: 8g
    memswap_limit: 8g
```

### 问题4: 端口冲突

**症状**: 端口已被占用

**解决方案**:
```bash
# 检查端口占用
lsof -i :8000
lsof -i :8001
lsof -i :8002

# 修改docker-compose.yml中的端口映射
ports:
  - "18000:8000"  # 使用其他端口
```

## 🔐 生产部署建议

### 1. 使用反向代理
```nginx
# Nginx配置示例
upstream opentalker {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://opentalker;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 添加认证
```python
# 在Gateway中添加API Key验证
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
```

### 3. 配置日志
```yaml
# docker-compose.yml
services:
  gateway:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. 健康检查和自动重启
```yaml
# docker-compose.yml
services:
  stt-service:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

## 📚 参考资料

- [Docker官方文档](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [OpenTalker GitHub](https://github.com/DDKTopLabs/OpenTalker)
- [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR)
- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)

---

**版本**: v0.3.0  
**更新时间**: 2026-02-04  
**维护者**: DDKTopLabs
