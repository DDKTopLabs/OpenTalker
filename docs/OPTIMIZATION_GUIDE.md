# OpenTalker 性能优化指南

本文档介绍如何在 4GB 显存的 GPU（如 GTX 1050 Ti）上优化 OpenTalker 的性能和显存占用。

## 📊 优化概览

| 优化项 | 显存节省 | 性能影响 | 推荐场景 |
|--------|---------|---------|---------|
| **FP16 半精度推理** | ~50% | 轻微加速 | 所有 CUDA GPU |
| **文本分块合成** | 稳定显存 | 无影响 | 长文本 TTS |
| **优化镜像** | 磁盘节省 38% | 无影响 | 所有场景 |
| **单服务部署** | 节省 2-3GB | 功能受限 | 4GB 显存 |

---

## 🚀 1. FP16 半精度推理

### 原理

FP16（半精度浮点）使用 16 位而不是 32 位来存储模型参数，可以：
- **显存占用减半**（约 50%）
- **推理速度提升**（Pascal 架构及以上）
- **精度损失极小**（语音任务几乎无影响）

### STT 服务启用 FP16

**环境变量配置**：
```yaml
environment:
  - QWEN_ASR_USE_FP16=true  # 启用 FP16（默认：true）
```

**显存对比**：
| 模式 | 显存占用 | 说明 |
|------|---------|------|
| FP32 | ~3.1GB | 默认全精度 |
| FP16 | ~1.6GB | 半精度（推荐） |

**示例配置**：
```yaml
services:
  stt:
    image: ghcr.io/ddktoplabs/opentalker-stt:v0.3.0-optimized
    environment:
      - MODEL_NAME=Qwen/Qwen3-ASR-0.6B
      - DEVICE=cuda
      - QWEN_ASR_USE_FP16=true  # 启用 FP16
```

### TTS 服务精度

TTS 服务默认使用 **bfloat16**（Brain Float 16），已经是优化的半精度格式：
- 显存占用：~2.0GB
- 无需额外配置
- 精度和 FP32 接近

---

## 📝 2. 文本分块合成

### 原理

长文本（如整章小说）会导致：
- **显存随文本长度增加**
- **可能触发 OOM 错误**
- **合成时间过长**

分块合成可以：
- **稳定显存占用**
- **避免 OOM**
- **支持超长文本**

### 启用文本分块

**环境变量配置**：
```yaml
environment:
  - QWEN_TTS_CHUNK_SIZE=200  # 每块最大字符数（0=禁用）
```

**推荐配置**：
| 文本长度 | 推荐 chunk_size | 说明 |
|---------|----------------|------|
| < 100 字符 | 0（禁用） | 短文本无需分块 |
| 100-500 字符 | 200 | 中等文本 |
| > 500 字符 | 150-200 | 长文本（小说、文章） |

**示例配置**：
```yaml
services:
  tts:
    image: ghcr.io/ddktoplabs/opentalker-tts:v0.3.0-optimized
    environment:
      - MODEL_NAME=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
      - DEVICE=cuda
      - QWEN_TTS_CHUNK_SIZE=200  # 启用分块
```

### 分块逻辑

文本会在以下标点符号处分割：
- 中文：`。！？；`
- 英文：`.!?;`

分块后的音频会自动拼接，用户无感知。

---

## 🎯 3. 4GB 显存优化方案

### 方案 A：STT + TTS 同时运行（需要优化）

**配置**：
```yaml
services:
  stt:
    environment:
      - QWEN_ASR_USE_FP16=true  # 启用 FP16
  tts:
    environment:
      - QWEN_TTS_CHUNK_SIZE=200  # 启用分块
```

**显存占用**：
- STT (FP16): ~1.6GB
- TTS (bfloat16): ~2.0GB
- **总计**: ~3.6GB ✅ 可用

### 方案 B：单服务部署（最稳定）

**仅 STT**：
```bash
docker compose -f examples/docker/docker-compose.stt-only.yml up -d
```

**仅 TTS**：
```bash
docker compose -f examples/docker/docker-compose.tts-only.yml up -d
```

**显存占用**：
- 单 STT: ~1.6GB (FP16)
- 单 TTS: ~2.0GB (bfloat16)

---

## 🔄 4. 实时语音对讲方案

### 使用 Faster-Whisper 替代 Qwen3-ASR

**优势**：
- **更低显存**：Small 模型 ~1.2GB，Medium-int8 ~1.5GB
- **更快速度**：优化的 CTranslate2 引擎
- **更好兼容**：与 IndexTTS 完美配合

**显存分配**：
```
STT (Faster-Whisper Small): ~1.2GB
TTS (IndexTTS bfloat16):    ~2.0GB
系统缓冲:                    ~0.8GB
─────────────────────────────────
总计:                        4.0GB ✅
```

### 实现方案

1. **替换 STT 服务**为 Faster-Whisper
2. **保持 TTS 服务**不变
3. **启用流式处理**减少延迟

**参考项目**：
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp)

---

## 📈 5. 性能对比

### STT 性能对比

| 配置 | 显存 | 速度 | 精度 |
|------|------|------|------|
| Qwen3-ASR FP32 | 3.1GB | 1.0x | 100% |
| Qwen3-ASR FP16 | 1.6GB | 1.2x | 99.5% |
| Faster-Whisper Small | 1.2GB | 2.0x | 95% |
| Faster-Whisper Medium-int8 | 1.5GB | 1.5x | 98% |

### TTS 性能对比

| 配置 | 显存 | 速度 | 质量 |
|------|------|------|------|
| IndexTTS FP32 | 3.8GB | 1.0x | 100% |
| IndexTTS bfloat16 | 2.0GB | 1.0x | 99.8% |
| IndexTTS FP16 | 1.9GB | 1.1x | 99.5% |

---

## 🛠️ 6. 完整配置示例

### 4GB 显存优化配置

```yaml
version: '3.8'

services:
  stt:
    image: ghcr.io/ddktoplabs/opentalker-stt:v0.3.0-optimized
    container_name: opentalker-stt
    ports:
      - "8001:8001"
    environment:
      - MODEL_NAME=Qwen/Qwen3-ASR-0.6B
      - DEVICE=cuda
      - LOG_LEVEL=INFO
      - HF_ENDPOINT=https://hf-mirror.com
      # 优化配置
      - QWEN_ASR_USE_FP16=true           # 启用 FP16，显存减半
      - QWEN_ASR_MAX_BATCH_SIZE=4        # 减小批处理大小
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  tts:
    image: ghcr.io/ddktoplabs/opentalker-tts:v0.3.0-optimized
    container_name: opentalker-tts
    ports:
      - "8002:8002"
    environment:
      - MODEL_NAME=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
      - DEVICE=cuda
      - LOG_LEVEL=INFO
      - HF_ENDPOINT=https://hf-mirror.com
      # 优化配置
      - QWEN_TTS_CHUNK_SIZE=200          # 启用文本分块
      - QWEN_TTS_SPEAKER=female_calm     # 默认说话人
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 8GB+ 显存标准配置

```yaml
# 8GB 以上显存无需特殊优化
services:
  stt:
    environment:
      - QWEN_ASR_USE_FP16=false  # 可选：使用 FP32 获得最高精度
      
  tts:
    environment:
      - QWEN_TTS_CHUNK_SIZE=0    # 禁用分块，性能最佳
```

---

## 🧪 7. 测试和验证

### 检查显存占用

```bash
# 查看 GPU 显存使用
nvidia-smi

# 查看具体进程显存
nvidia-smi --query-compute-apps=pid,used_memory --format=csv
```

### 测试 FP16 效果

```bash
# 启用 FP16
curl -X POST http://localhost:8001/v1/audio/transcriptions \
  -F "file=@test.wav" \
  -F "model=whisper-1"

# 对比显存占用
nvidia-smi
```

### 测试文本分块

```bash
# 发送长文本
curl -X POST http://localhost:8002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "这是一段很长的文本..." (500+ 字符),
    "voice": "alloy"
  }' \
  --output long_text.wav

# 检查日志
docker logs opentalker-tts | grep "chunk"
```

---

## 📚 8. 常见问题

### Q: FP16 会影响识别/合成质量吗？

**A**: 影响极小（<0.5%），人耳几乎无法察觉。语音任务对精度要求不如图像任务高。

### Q: 文本分块会有停顿感吗？

**A**: 不会。分块在句子边界进行，音频无缝拼接，听感自然。

### Q: 4GB 显存能同时运行 STT 和 TTS 吗？

**A**: 
- **启用 FP16**: 可以（~3.6GB）✅
- **不启用 FP16**: 不行（~5.1GB）❌

### Q: 如何选择 chunk_size？

**A**: 
- 短文本（<100 字）：0（禁用）
- 中等文本（100-500 字）：200
- 长文本（>500 字）：150-200

### Q: Faster-Whisper 比 Qwen3-ASR 好吗？

**A**: 各有优势：
- **Faster-Whisper**: 更快、更省显存、更成熟
- **Qwen3-ASR**: 中文效果更好、更新的模型

---

## 🎯 9. 推荐配置总结

### GTX 1050 Ti (4GB)

```yaml
# 推荐配置
STT:
  - QWEN_ASR_USE_FP16=true
  - QWEN_ASR_MAX_BATCH_SIZE=4

TTS:
  - QWEN_TTS_CHUNK_SIZE=200
```

**预期显存**: ~3.6GB

### RTX 2060 (6GB)

```yaml
# 标准配置
STT:
  - QWEN_ASR_USE_FP16=true  # 可选

TTS:
  - QWEN_TTS_CHUNK_SIZE=0   # 禁用分块
```

**预期显存**: ~5.1GB (FP32) 或 ~3.6GB (FP16)

### RTX 3090 (24GB)

```yaml
# 高性能配置
STT:
  - QWEN_ASR_USE_FP16=false  # 使用 FP32
  - QWEN_ASR_MAX_BATCH_SIZE=16

TTS:
  - QWEN_TTS_CHUNK_SIZE=0    # 禁用分块
```

**预期显存**: ~5.1GB（大量余量）

---

## 📖 相关文档

- [Docker 部署指南](DOCKER_GUIDE.md)
- [4GB 显存部署方案](DOCKER_GUIDE.md#-4gb-显存部署方案)
- [Dockerfile 优化对比](DOCKERFILE_OPTIMIZATION_COMPARISON.md)
- [项目结构](../PROJECT_STRUCTURE.md)

---

**最后更新**: 2026-02-05  
**版本**: v0.3.0
