# Docker Compose 示例

本目录包含不同场景的 Docker Compose 配置文件。

## 📁 文件说明

### docker-compose.ghcr.yml
**使用 GHCR 公开镜像部署（推荐）**

适用于：
- 快速部署，无需构建镜像
- 国际网络环境
- 生产环境
- 8GB+ 显存的 GPU

使用方法：
```bash
docker-compose -f examples/docker/docker-compose.ghcr.yml up -d
```

镜像源：
- `ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0`
- `ghcr.io/ddktoplabs/opentalker-stt:v0.3.0`
- `ghcr.io/ddktoplabs/opentalker-tts:v0.3.0`

### docker-compose.china.yml
**使用国内镜像源部署（国内用户推荐）**

适用于：
- 国内网络环境
- 需要加速镜像下载
- 快速部署
- 8GB+ 显存的 GPU

使用方法：
```bash
docker-compose -f examples/docker/docker-compose.china.yml up -d
```

镜像源：
- `ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0`
- `ghcr.1ms.run/ddktoplabs/opentalker-stt:v0.3.0`
- `ghcr.1ms.run/ddktoplabs/opentalker-tts:v0.3.0`

### docker-compose.stt-only.yml ⭐ NEW
**仅 STT 服务部署（4GB 显存兼容）**

适用于：
- 4GB 显存的 GPU（如 GTX 1050 Ti）
- 只需要语音识别功能
- 优化镜像，体积减少 38%

使用方法：
```bash
docker-compose -f examples/docker/docker-compose.stt-only.yml up -d
```

镜像：
- `ghcr.io/ddktoplabs/opentalker-stt:v0.3.0-optimized` (3.44GB)

显存占用：约 3.1GB

### docker-compose.tts-only.yml ⭐ NEW
**仅 TTS 服务部署（4GB 显存兼容）**

适用于：
- 4GB 显存的 GPU（如 GTX 1050 Ti）
- 只需要语音合成功能
- 优化镜像，体积减少 38%

使用方法：
```bash
docker-compose -f examples/docker/docker-compose.tts-only.yml up -d
```

镜像：
- `ghcr.io/ddktoplabs/opentalker-tts:v0.3.0-optimized` (3.39GB)

显存占用：约 2.2GB

### docker-compose.4gb-optimized.yml ⭐⭐ NEW
**4GB 显存优化配置（STT + TTS 同时运行）**

适用于：
- 4GB 显存的 GPU（如 GTX 1050 Ti）
- 需要同时使用 STT 和 TTS
- 启用 FP16 和文本分块优化

使用方法：
```bash
docker-compose -f examples/docker/docker-compose.4gb-optimized.yml up -d
```

镜像：
- `ghcr.io/ddktoplabs/opentalker-stt:v0.3.0-optimized` (3.44GB)
- `ghcr.io/ddktoplabs/opentalker-tts:v0.3.0-optimized` (3.39GB)
- `ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0` (82.5MB)

**优化特性**：
- ✅ FP16 半精度推理（STT 显存减半）
- ✅ 文本分块合成（TTS 稳定显存）
- ✅ 总显存占用：~3.6GB

**显存占用**：
- STT (FP16): ~1.6GB
- TTS (bfloat16): ~2.0GB
- 总计: ~3.6GB ✅ 4GB GPU 可用

详细说明：[性能优化指南](../../docs/OPTIMIZATION_GUIDE.md)

### docker-compose.workspace.yml
**微服务架构部署**

适用于：
- 开发环境
- 需要修改代码
- 微服务分离部署
- 自定义构建
- 8GB+ 显存的 GPU

使用方法：
```bash
docker-compose -f examples/docker/docker-compose.workspace.yml up -d
```

特点：
- Gateway、STT、TTS 分离为独立服务
- 每个服务独立构建
- 支持独立扩展和更新

## 🚀 快速选择

### 我应该使用哪个配置？

| 场景 | 推荐配置 | 原因 |
|------|---------|------|
| **4GB 显存 GPU（GTX 1050 Ti）- 需要 STT+TTS** | `docker-compose.4gb-optimized.yml` ⭐⭐ | FP16+分块优化，显存 3.6GB |
| **4GB 显存 GPU - 仅需 STT** | `docker-compose.stt-only.yml` | 单服务部署，优化镜像 |
| **4GB 显存 GPU - 仅需 TTS** | `docker-compose.tts-only.yml` | 单服务部署，优化镜像 |
| 国内用户快速部署（8GB+ 显存） | `docker-compose.china.yml` | 使用国内镜像源，下载速度快 |
| 国际用户快速部署（8GB+ 显存） | `docker-compose.ghcr.yml` | 使用官方 GHCR 镜像 |
| 开发和调试 | `docker-compose.workspace.yml` | 支持代码修改和独立构建 |
| 生产环境（8GB+ 显存） | `docker-compose.ghcr.yml` | 使用稳定的公开镜像 |

### 显存要求对照表

| GPU 型号 | 显存 | 推荐配置 | 说明 |
|---------|------|---------|------|
| GTX 1050 Ti | 4GB | `stt-only.yml` 或 `tts-only.yml` | 只能运行单个服务 |
| GTX 1060 6GB | 6GB | `stt-only.yml` 或 `tts-only.yml` | 建议单服务，更稳定 |
| RTX 2060 | 6GB | `stt-only.yml` 或 `tts-only.yml` | 建议单服务，更稳定 |
| RTX 2080 Ti | 11GB | `ghcr.yml` 或 `china.yml` | 可同时运行 STT + TTS |
| RTX 3090 | 24GB | `ghcr.yml` 或 `china.yml` | 可同时运行 STT + TTS |

## 📝 配置对比

| 特性 | ghcr.yml | china.yml | stt-only.yml | tts-only.yml | workspace.yml |
|------|----------|-----------|--------------|--------------|---------------|
| 镜像来源 | GHCR 官方 | GHCR 国内镜像 | GHCR 优化版 | GHCR 优化版 | 本地构建 |
| 镜像大小 | 5.55GB + 5.49GB | 5.55GB + 5.49GB | 3.44GB | 3.39GB | N/A |
| 下载速度（国内） | 慢 | 快 ⚡ | 快 ⚡ | 快 ⚡ | N/A |
| 下载速度（国际） | 快 | 中等 | 快 | 快 | N/A |
| 最低显存要求 | 8GB | 8GB | 4GB ✅ | 4GB ✅ | 8GB |
| 是否需要构建 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 支持代码修改 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 微服务分离 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 适合生产环境 | ✅ | ✅ | ✅ | ✅ | ❌ |

## 🔧 自定义配置

### 修改端口

编辑配置文件中的 `ports` 部分：

```yaml
services:
  gateway:
    ports:
      - "8080:8000"  # 将 8000 改为 8080
```

### 修改环境变量

编辑配置文件中的 `environment` 部分：

```yaml
services:
  stt-service:
    environment:
      - LOG_LEVEL=DEBUG  # 修改日志级别
      - QWEN_ASR_MAX_BATCH_SIZE=4  # 修改批处理大小
```

### 持久化模型缓存

添加 volume 挂载：

```yaml
services:
  stt-service:
    volumes:
      - ./models:/models
      - ./cache:/root/.cache  # 持久化模型缓存
```

## 📚 相关文档

- [Docker 镜像使用指南](../../docs/DOCKER_IMAGES_GUIDE.md)
- [Docker 部署指南](../../docs/DOCKER_GUIDE.md)
- [微服务架构指南](../../docs/README.workspace.md)

## ⚠️ 注意事项

1. **GPU 要求**：所有配置都需要 NVIDIA GPU 和 NVIDIA Container Toolkit
2. **显存限制**：
   - **4GB 显存**（GTX 1050 Ti）：只能运行单个服务，使用 `stt-only.yml` 或 `tts-only.yml`
   - **8GB+ 显存**：可以同时运行 STT + TTS 服务
3. **网络要求**：首次启动需要下载模型（约 1.8GB）
4. **端口冲突**：确保 8000-8002 端口未被占用
5. **优化镜像**：`-optimized` 标签的镜像体积减少 38%，功能完全相同

## 🐛 故障排查

### 镜像拉取失败

**问题**：`unauthorized` 或 `connection timeout`

**解决**：
- 国内用户使用 `docker-compose.china.yml`
- 检查网络连接
- 尝试手动拉取镜像：
  ```bash
  docker pull ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0
  ```

### GPU 不可用

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

### 端口被占用

**问题**：`port is already allocated`

**解决**：
- 修改配置文件中的端口映射
- 或停止占用端口的服务

---

**最后更新**: 2026-02-05  
**版本**: v0.3.0
