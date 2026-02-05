# GitHub Container Registry 镜像推送状态

## 推送时间
**开始时间**: 2026-02-04 21:05  
**最后更新**: 2026-02-04 22:00  
**状态**: 部分完成

## 镜像列表

### ✅ Gateway (已完成)
- **镜像**: `ghcr.io/ddktoplabs/opentalker-gateway:latest`
- **镜像**: `ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0`
- **大小**: 325MB
- **Digest**: `sha256:eb6ef88fbd92e5c31dce4b178987bf307728d2a026cae9dc6983f22bf735c409`
- **状态**: ✅ 推送完成并验证

### ✅ STT Service (已完成)
- **镜像**: `ghcr.io/ddktoplabs/opentalker-stt:latest`
- **镜像**: `ghcr.io/ddktoplabs/opentalker-stt:v0.3.0`
- **大小**: 5.55GB
- **Digest**: `sha256:dc092d78b82fa456a1c2f6b7fbc16662991b7a0ef001399f83fc9a9fb5755bff`
- **状态**: ✅ 推送完成并验证

### ⏳ TTS Service (推送中)
- **镜像**: `ghcr.io/ddktoplabs/opentalker-tts:latest`
- **镜像**: `ghcr.io/ddktoplabs/opentalker-tts:v0.3.0`
- **大小**: 5.49GB
- **状态**: ⏳ 正在推送 (PID: 7384)
- **日志**: `/tmp/docker_push_tts_final.log`

## 检查推送状态

在 WSL 上运行以下命令检查推送进度：

```bash
ssh -p 2222 devocy@192.168.31.77

# 查看推送日志
tail -f /tmp/docker_push.log

# 检查是否完成
cat /tmp/docker_push_complete.txt
```

## 使用镜像

### 拉取镜像

```bash
# Gateway
docker pull ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0

# STT Service
docker pull ghcr.io/ddktoplabs/opentalker-stt:v0.3.0

# TTS Service
docker pull ghcr.io/ddktoplabs/opentalker-tts:v0.3.0
```

### 使用 Docker Compose

更新 `docker-compose.yml` 使用 GHCR 镜像：

```yaml
version: '3.8'

services:
  gateway:
    image: ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0
    ports:
      - "8000:8000"
    environment:
      - GATEWAY_HOST=0.0.0.0
      - GATEWAY_PORT=8000
      - STT_SERVICE_URL=http://stt-service:8001
      - TTS_SERVICE_URL=http://tts-service:8002
    depends_on:
      - stt-service
      - tts-service
    networks:
      - opentalker-network

  stt-service:
    image: ghcr.io/ddktoplabs/opentalker-stt:v0.3.0
    ports:
      - "8001:8001"
    environment:
      - SERVICE_HOST=0.0.0.0
      - SERVICE_PORT=8001
      - QWEN_ASR_MODEL=Qwen/Qwen3-ASR-0.6B
      - QWEN_ASR_DEVICE=cuda:0
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

  tts-service:
    image: ghcr.io/ddktoplabs/opentalker-tts:v0.3.0
    ports:
      - "8002:8002"
    environment:
      - SERVICE_HOST=0.0.0.0
      - SERVICE_PORT=8002
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

networks:
  opentalker-network:
    driver: bridge
```

### 快速启动

```bash
# 使用 GHCR 镜像启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 镜像信息

### 镜像仓库
- **Registry**: ghcr.io (GitHub Container Registry)
- **组织**: ddktoplabs
- **项目**: OpenTalker
- **可见性**: Public (公开)

### 镜像标签
- `latest` - 最新版本
- `v0.3.0` - 稳定版本

### 访问权限
这些镜像是公开的，任何人都可以拉取使用，无需认证。

## 镜像大小对比

| 服务 | 镜像大小 | 压缩大小 | 推送时间（估计） |
|------|---------|---------|----------------|
| Gateway | 325MB | 82.5MB | ~1分钟 |
| STT Service | 5.55GB | 5.55GB | ~10-15分钟 |
| TTS Service | 5.49GB | 5.49GB | ~10-15分钟 |

## 推送命令记录

```bash
# 登录 GHCR
echo 'ghp_***' | docker login ghcr.io -u devocy --password-stdin

# 标记镜像
docker tag opentalker-gateway:latest ghcr.io/ddktoplabs/opentalker-gateway:latest
docker tag opentalker-gateway:latest ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0
docker tag opentalker-stt-service:latest ghcr.io/ddktoplabs/opentalker-stt:latest
docker tag opentalker-stt-service:latest ghcr.io/ddktoplabs/opentalker-stt:v0.3.0
docker tag opentalker-tts-service:latest ghcr.io/ddktoplabs/opentalker-tts:latest
docker tag opentalker-tts-service:latest ghcr.io/ddktoplabs/opentalker-tts:v0.3.0

# 推送镜像
docker push ghcr.io/ddktoplabs/opentalker-gateway:latest
docker push ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0
docker push ghcr.io/ddktoplabs/opentalker-stt:latest
docker push ghcr.io/ddktoplabs/opentalker-stt:v0.3.0
docker push ghcr.io/ddktoplabs/opentalker-tts:latest
docker push ghcr.io/ddktoplabs/opentalker-tts:v0.3.0
```

## 验证推送

推送完成后，可以在以下位置查看镜像：

- Gateway: https://github.com/orgs/DDKTopLabs/packages/container/package/opentalker-gateway
- STT: https://github.com/orgs/DDKTopLabs/packages/container/package/opentalker-stt
- TTS: https://github.com/orgs/DDKTopLabs/packages/container/package/opentalker-tts

## 注意事项

1. **网络速度**: 推送大型镜像需要稳定的网络连接
2. **存储空间**: GHCR 对公开仓库有存储限制
3. **版本管理**: 建议使用语义化版本标签（如 v0.3.0）
4. **安全性**: Token 已用于推送，请妥善保管

## 下一步

推送完成后：
1. ✅ 验证镜像可以正常拉取
2. ✅ 更新 README.md 添加 GHCR 使用说明
3. ✅ 创建 docker-compose.ghcr.yml 示例文件
4. ✅ 添加 CI/CD 自动推送流程

---

**更新时间**: 2026-02-04 21:10  
**状态**: STT 和 TTS 镜像推送中，预计 10-15 分钟完成
