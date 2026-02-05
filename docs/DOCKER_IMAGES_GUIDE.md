# OpenTalker Docker 镜像使用指南

## 📦 镜像仓库

所有镜像已发布到 GitHub Container Registry (GHCR)，**完全公开**，无需认证即可拉取。

### 镜像列表

| 服务 | 镜像地址 | 大小 | 说明 |
|------|---------|------|------|
| Gateway | `ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0` | 82.5MB | API 网关服务 |
| STT Service | `ghcr.io/ddktoplabs/opentalker-stt:v0.3.0` | 5.55GB | 语音识别服务 (Qwen3-ASR) |
| TTS Service | `ghcr.io/ddktoplabs/opentalker-tts:v0.3.0` | 5.49GB | 语音合成服务 (Qwen3-TTS) |

### 镜像标签

- `latest` - 最新版本
- `v0.3.0` - 稳定版本（推荐）

---

## 🚀 快速开始

### 方法 1：使用官方 GHCR（国际）

```bash
# 拉取镜像
docker pull ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0
docker pull ghcr.io/ddktoplabs/opentalker-stt:v0.3.0
docker pull ghcr.io/ddktoplabs/opentalker-tts:v0.3.0

# 使用 Docker Compose 启动
docker-compose -f docker-compose.ghcr.yml up -d
```

### 方法 2：使用国内镜像源（推荐）🇨🇳

**国内用户可以使用 `ghcr.1ms.run` 镜像源加速下载：**

```bash
# 拉取镜像（使用国内镜像源）
docker pull ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0
docker pull ghcr.1ms.run/ddktoplabs/opentalker-stt:v0.3.0
docker pull ghcr.1ms.run/ddktoplabs/opentalker-tts:v0.3.0

# 重新标记为标准名称（可选）
docker tag ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0 ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0
docker tag ghcr.1ms.run/ddktoplabs/opentalker-stt:v0.3.0 ghcr.io/ddktoplabs/opentalker-stt:v0.3.0
docker tag ghcr.1ms.run/ddktoplabs/opentalker-tts:v0.3.0 ghcr.io/ddktoplabs/opentalker-tts:v0.3.0
```

### 方法 3：使用国内镜像源的 Docker Compose

创建 `docker-compose.china.yml`：

```yaml
version: '3.8'

services:
  gateway:
    image: ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0
    container_name: opentalker-gateway
    ports:
      - "8000:8000"
    environment:
      - GATEWAY_HOST=0.0.0.0
      - GATEWAY_PORT=8000
      - LOG_LEVEL=INFO
      - STT_SERVICE_URL=http://stt-service:8001
      - TTS_SERVICE_URL=http://tts-service:8002
      - STT_TIMEOUT=120
      - TTS_TIMEOUT=180
    depends_on:
      - stt-service
      - tts-service
    networks:
      - opentalker-network
    restart: unless-stopped

  stt-service:
    image: ghcr.1ms.run/ddktoplabs/opentalker-stt:v0.3.0
    container_name: opentalker-stt
    ports:
      - "8001:8001"
    environment:
      - SERVICE_HOST=0.0.0.0
      - SERVICE_PORT=8001
      - LOG_LEVEL=INFO
      - QWEN_ASR_MODEL=Qwen/Qwen3-ASR-0.6B
      - QWEN_ASR_DEVICE=cuda:0
      - QWEN_ASR_MAX_BATCH_SIZE=8
      - MAX_UPLOAD_SIZE=52428800
      - HF_ENDPOINT=https://hf-mirror.com
    volumes:
      - ./models:/models
      - ./stt-service/tmp:/app/tmp
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - opentalker-network
    restart: unless-stopped

  tts-service:
    image: ghcr.1ms.run/ddktoplabs/opentalker-tts:v0.3.0
    container_name: opentalker-tts
    ports:
      - "8002:8002"
    environment:
      - SERVICE_HOST=0.0.0.0
      - SERVICE_PORT=8002
      - LOG_LEVEL=INFO
      - QWEN_TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
      - QWEN_TTS_DEVICE=cuda:0
      - HF_ENDPOINT=https://hf-mirror.com
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - opentalker-network
    restart: unless-stopped

networks:
  opentalker-network:
    driver: bridge
```

启动服务：

```bash
docker-compose -f docker-compose.china.yml up -d
```

---

## 🌍 镜像源对比

| 镜像源 | 地址 | 适用地区 | 速度 |
|--------|------|---------|------|
| **官方 GHCR** | `ghcr.io` | 国际 | 国外快，国内慢 |
| **国内镜像** | `ghcr.1ms.run` | 中国大陆 | 国内快 ⚡ |

### 其他可用的国内镜像源

```bash
# 1ms.run 镜像源（推荐）
ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0

# 其他镜像源（如果 1ms.run 不可用）
# 注意：以下镜像源可能需要自行验证可用性
ghcr.dockerproxy.com/ddktoplabs/opentalker-gateway:v0.3.0
```

---

## 📝 使用说明

### 1. 准备环境

**系统要求**：
- Ubuntu 22.04 或更高版本
- Docker 20.10+ 
- Docker Compose v2.0+
- NVIDIA GPU（支持 CUDA 12.1）
- NVIDIA Container Toolkit

**安装 NVIDIA Container Toolkit**：

```bash
# 添加 NVIDIA 仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 重启 Docker
sudo systemctl restart docker
```

### 2. 创建项目目录

```bash
mkdir -p ~/opentalker
cd ~/opentalker
mkdir -p models stt-service/tmp
```

### 3. 下载 Docker Compose 配置

```bash
# 国际用户
wget https://raw.githubusercontent.com/DDKTopLabs/OpenTalker/main/docker-compose.ghcr.yml

# 国内用户（使用镜像源）
wget https://raw.githubusercontent.com/DDKTopLabs/OpenTalker/main/docker-compose.china.yml
```

### 4. 启动服务

```bash
# 国际用户
docker-compose -f docker-compose.ghcr.yml up -d

# 国内用户
docker-compose -f docker-compose.china.yml up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

### 5. 验证服务

```bash
# 检查健康状态
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# 测试 STT（语音识别）
curl -X POST http://localhost:8001/v1/audio/transcriptions \
  -F "file=@test_audio.wav" \
  -F "model=qwen3-asr"

# 测试 TTS（语音合成）
curl -X POST http://localhost:8002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"你好世界","voice":"default","model":"qwen3-tts"}' \
  --output output.wav
```

---

## 🔧 配置说明

### 环境变量

#### Gateway 服务

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GATEWAY_HOST` | `0.0.0.0` | 监听地址 |
| `GATEWAY_PORT` | `8000` | 监听端口 |
| `STT_SERVICE_URL` | `http://stt-service:8001` | STT 服务地址 |
| `TTS_SERVICE_URL` | `http://tts-service:8002` | TTS 服务地址 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

#### STT 服务

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SERVICE_HOST` | `0.0.0.0` | 监听地址 |
| `SERVICE_PORT` | `8001` | 监听端口 |
| `QWEN_ASR_MODEL` | `Qwen/Qwen3-ASR-0.6B` | 模型名称 |
| `QWEN_ASR_DEVICE` | `cuda:0` | 使用的 GPU |
| `HF_ENDPOINT` | `https://hf-mirror.com` | Hugging Face 镜像 |

#### TTS 服务

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SERVICE_HOST` | `0.0.0.0` | 监听地址 |
| `SERVICE_PORT` | `8002` | 监听端口 |
| `QWEN_TTS_MODEL` | `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` | 模型名称 |
| `QWEN_TTS_DEVICE` | `cuda:0` | 使用的 GPU |
| `HF_ENDPOINT` | `https://hf-mirror.com` | Hugging Face 镜像 |

### 模型下载

**模型会在首次启动时自动下载**，缓存在容器内的 `/root/.cache/huggingface` 目录。

如果想持久化模型缓存，可以添加 volume 挂载：

```yaml
volumes:
  - ./models:/models
  - ./cache:/root/.cache  # 持久化模型缓存
```

---

## 🐛 故障排查

### 1. 镜像拉取失败

**问题**：`unauthorized` 或 `connection timeout`

**解决**：
- 国际用户：检查网络连接，或使用代理
- 国内用户：使用 `ghcr.1ms.run` 镜像源

### 2. GPU 不可用

**问题**：容器内无法使用 GPU

**解决**：
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# 重新安装 NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 3. 模型下载慢

**问题**：首次启动时模型下载很慢

**解决**：
- 使用 Hugging Face 镜像：`HF_ENDPOINT=https://hf-mirror.com`
- 或手动下载模型后挂载到容器

### 4. 显存不足

**问题**：`CUDA out of memory`

**解决**：
- 确保 GPU 有至少 4GB 显存
- 关闭其他占用 GPU 的程序
- 降低 batch size：`QWEN_ASR_MAX_BATCH_SIZE=4`

---

## 📊 性能优化

### GPU 显存优化

**GTX 1050 Ti (4GB)** - 单服务模式：
```yaml
# 只运行 STT 或 TTS，不要同时运行
docker-compose up -d gateway stt-service
# 或
docker-compose up -d gateway tts-service
```

**RTX 2080 Ti (22GB)** - 全服务模式：
```yaml
# 可以同时运行所有服务
docker-compose up -d
```

### 网络优化

**国内用户**：
- 使用 `ghcr.1ms.run` 镜像源
- 使用 `HF_ENDPOINT=https://hf-mirror.com`
- 配置 Docker 镜像加速器

---

## 📚 相关链接

- **GitHub 仓库**: https://github.com/DDKTopLabs/OpenTalker
- **镜像仓库**: 
  - Gateway: https://github.com/orgs/DDKTopLabs/packages/container/package/opentalker-gateway
  - STT: https://github.com/orgs/DDKTopLabs/packages/container/package/opentalker-stt
  - TTS: https://github.com/orgs/DDKTopLabs/packages/container/package/opentalker-tts
- **国内镜像源**: https://1ms.run

---

## 📄 许可证

本项目遵循 MIT 许可证。

---

**最后更新**: 2026-02-04  
**版本**: v0.3.0  
**状态**: ✅ 所有镜像已公开发布
