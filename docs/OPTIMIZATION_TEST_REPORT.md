# OpenTalker 性能优化测试报告

## 📊 测试环境

- **测试日期**: 2026-02-05
- **测试服务器**: 192.168.31.36
- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM)
- **系统**: Ubuntu 22.04
- **Docker**: 28.5.1

---

## ✅ 已完成的优化

### 1. 镜像优化（已测试 ✅）

**优化内容**:
- 基础镜像: `nvidia/cuda:12.1.0-cudnn8-runtime` → `nvidia/cuda:12.1.0-base`
- 移除不必要的构建工具
- 清理 Python 缓存文件

**测试结果**:
| 指标 | 标准版 | 优化版 | 改进 |
|------|--------|--------|------|
| 压缩大小 | 5.55GB | 3.44GB | **-38%** |
| 解压大小 | 10.1GB | 6.76GB | **-33%** |
| 显存占用 | 3.1GB | 3.1GB | 相同 |
| 功能 | 完整 | 完整 | 相同 |

**测试命令**:
```bash
# 部署优化镜像
docker pull ghcr.io/ddktoplabs/opentalker-stt:v0.3.0-optimized
docker run -d --gpus all -p 8001:8001 \
  -e MODEL_NAME=Qwen/Qwen3-ASR-0.6B \
  -e DEVICE=cuda \
  ghcr.io/ddktoplabs/opentalker-stt:v0.3.0-optimized

# 检查显存
nvidia-smi
```

**测试输出**:
```
NAME                       STATUS    VRAM
opentalker-stt-optimized   healthy   3122 MiB / 4096 MiB
```

✅ **结论**: 优化镜像在 4GB GPU 上运行正常，显存占用 3.1GB

---

### 2. FP16 半精度优化（代码已实现 ⏳）

**实现内容**:
- ✅ 添加 `QWEN_ASR_USE_FP16` 配置项
- ✅ 实现模型 FP16 转换逻辑
- ✅ 自动检测 CUDA 设备
- ⏳ 需要重新构建镜像

**预期效果**:
| 指标 | FP32 | FP16 | 改进 |
|------|------|------|------|
| 显存占用 | 3.1GB | ~1.6GB | **-50%** |
| 推理速度 | 1.0x | ~1.2x | **+20%** |
| 精度损失 | 0% | <0.5% | 可忽略 |

**代码位置**:
- `stt-service/app/config.py` - 配置项
- `stt-service/app/service.py` - FP16 转换逻辑

**使用方法**:
```yaml
environment:
  - QWEN_ASR_USE_FP16=true  # 启用 FP16
```

**状态**: ⏳ 代码已提交，需要重新构建镜像测试

---

### 3. TTS 文本分块（代码已实现 ⏳）

**实现内容**:
- ✅ 添加 `QWEN_TTS_CHUNK_SIZE` 配置项
- ✅ 实现智能分句算法（中英文标点）
- ✅ 实现分块合成和音频拼接
- ⏳ 需要重新构建镜像

**预期效果**:
- 稳定显存占用（避免长文本波动）
- 支持超长文本（整章小说）
- 无缝音频拼接

**代码位置**:
- `tts-service/app/config.py` - 配置项
- `tts-service/app/service.py` - 分块逻辑

**使用方法**:
```yaml
environment:
  - QWEN_TTS_CHUNK_SIZE=200  # 每块最大 200 字符
```

**状态**: ⏳ 代码已提交，需要重新构建镜像测试

---

## 📋 下一步测试计划

### 步骤 1: 构建包含优化的新镜像

在 192.168.31.77 (构建服务器) 上：

```bash
# 拉取最新代码
cd ~/OpenTalker
git pull

# 构建 FP16 优化的 STT 镜像
docker build -f stt-service/Dockerfile.optimized \
  -t ghcr.io/ddktoplabs/opentalker-stt:v0.3.1-fp16 \
  stt-service/

# 构建文本分块优化的 TTS 镜像
docker build -f tts-service/Dockerfile.optimized \
  -t ghcr.io/ddktoplabs/opentalker-tts:v0.3.1-chunked \
  tts-service/

# 推送到 GHCR
docker push ghcr.io/ddktoplabs/opentalker-stt:v0.3.1-fp16
docker push ghcr.io/ddktoplabs/opentalker-tts:v0.3.1-chunked
```

### 步骤 2: 测试 FP16 优化

在 192.168.31.36 (测试机) 上：

```bash
# 拉取 FP16 镜像
docker pull ghcr.io/ddktoplabs/opentalker-stt:v0.3.1-fp16

# 启动服务
docker run -d --gpus all -p 8001:8001 \
  -e MODEL_NAME=Qwen/Qwen3-ASR-0.6B \
  -e DEVICE=cuda \
  -e QWEN_ASR_USE_FP16=true \
  --name stt-fp16-test \
  ghcr.io/ddktoplabs/opentalker-stt:v0.3.1-fp16

# 等待模型加载
sleep 60

# 检查显存占用
nvidia-smi --query-compute-apps=pid,used_memory --format=csv

# 检查服务状态
curl http://localhost:8001/health | jq

# 检查日志中的 FP16 信息
docker logs stt-fp16-test | grep -i fp16
```

**预期输出**:
```
2026-02-05 XX:XX:XX - app.service - INFO - FP16 enabled: True
2026-02-05 XX:XX:XX - app.service - INFO - Converting model to FP16 (half precision)
2026-02-05 XX:XX:XX - app.service - INFO - FP16 conversion complete - VRAM usage reduced by ~50%

VRAM: ~1600 MiB (vs 3100 MiB without FP16)
```

### 步骤 3: 测试文本分块

```bash
# 拉取分块镜像
docker pull ghcr.io/ddktoplabs/opentalker-tts:v0.3.1-chunked

# 启动服务
docker run -d --gpus all -p 8002:8002 \
  -e MODEL_NAME=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice \
  -e DEVICE=cuda \
  -e QWEN_TTS_CHUNK_SIZE=200 \
  --name tts-chunked-test \
  ghcr.io/ddktoplabs/opentalker-tts:v0.3.1-chunked

# 测试长文本合成
curl -X POST http://localhost:8002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "这是一段很长的测试文本...(500+ 字符)",
    "voice": "alloy"
  }' \
  --output long_text.wav

# 检查日志中的分块信息
docker logs tts-chunked-test | grep -i chunk
```

**预期输出**:
```
2026-02-05 XX:XX:XX - app.service - INFO - Text exceeds chunk size (523 > 200), using chunked synthesis
2026-02-05 XX:XX:XX - app.service - INFO - Split text (523 chars) into 3 chunks
2026-02-05 XX:XX:XX - app.service - INFO - Synthesizing chunk 1/3: 198 chars
2026-02-05 XX:XX:XX - app.service - INFO - Synthesizing chunk 2/3: 200 chars
2026-02-05 XX:XX:XX - app.service - INFO - Synthesizing chunk 3/3: 125 chars
2026-02-05 XX:XX:XX - app.service - INFO - Concatenating 3 audio chunks
2026-02-05 XX:XX:XX - app.service - INFO - Chunked synthesis completed: XXXXX bytes
```

### 步骤 4: 测试 STT + TTS 同时运行

```bash
# 使用 4GB 优化配置
cd ~/OpenTalker
docker compose -f examples/docker/docker-compose.4gb-optimized.yml up -d

# 检查总显存占用
nvidia-smi

# 检查两个服务状态
curl http://localhost:8001/health | jq
curl http://localhost:8002/health | jq
```

**预期显存占用**:
```
STT (FP16):      ~1.6GB
TTS (bfloat16):  ~2.0GB
─────────────────────────
总计:            ~3.6GB ✅ (4GB GPU 可用)
```

---

## 📊 预期性能对比

### 显存占用对比

| 配置 | STT | TTS | 总计 | 4GB GPU |
|------|-----|-----|------|---------|
| **当前优化版** | 3.1GB | 2.0GB | 5.1GB | ❌ 超出 |
| **FP16 优化** | 1.6GB | 2.0GB | 3.6GB | ✅ 可用 |
| **单 STT (FP16)** | 1.6GB | - | 1.6GB | ✅ 可用 |
| **单 TTS** | - | 2.0GB | 2.0GB | ✅ 可用 |

### 镜像大小对比

| 版本 | STT | TTS | 总计 |
|------|-----|-----|------|
| 标准版 | 5.55GB | 5.49GB | 11.04GB |
| 优化版 (v0.3.0) | 3.44GB | 3.39GB | 6.83GB |
| FP16 版 (v0.3.1) | 3.44GB | 3.39GB | 6.83GB |

*注: FP16 是运行时优化，不影响镜像大小*

---

## 📝 测试检查清单

### FP16 优化测试

- [ ] 构建包含 FP16 代码的镜像
- [ ] 部署到 GTX 1050 Ti
- [ ] 验证显存从 3.1GB 降至 ~1.6GB
- [ ] 测试 API 功能正常
- [ ] 测试识别精度（对比 FP32）
- [ ] 测试推理速度
- [ ] 检查日志中的 FP16 信息

### 文本分块测试

- [ ] 构建包含分块代码的镜像
- [ ] 部署到 GTX 1050 Ti
- [ ] 测试短文本（<100 字）- 不分块
- [ ] 测试中等文本（100-500 字）- 分块
- [ ] 测试长文本（>500 字）- 分块
- [ ] 验证音频无缝拼接
- [ ] 检查显存稳定性
- [ ] 检查日志中的分块信息

### 综合测试

- [ ] STT + TTS 同时运行
- [ ] 总显存 < 4GB
- [ ] 两个服务都健康
- [ ] API 功能正常
- [ ] 长时间稳定性测试

---

## 🎯 成功标准

### FP16 优化

✅ **成功标准**:
1. 显存占用降至 1.6GB ± 0.2GB
2. API 功能完全正常
3. 识别精度损失 < 1%
4. 推理速度提升 > 10%

### 文本分块

✅ **成功标准**:
1. 长文本（>500 字）显存稳定
2. 音频拼接无明显停顿
3. 支持 1000+ 字符文本
4. 分块逻辑正确（按标点分句）

### 综合测试

✅ **成功标准**:
1. STT + TTS 总显存 < 4GB
2. 两个服务同时健康运行
3. API 响应正常
4. 长时间运行稳定（> 1 小时）

---

## 📚 相关文档

- [性能优化指南](OPTIMIZATION_GUIDE.md)
- [Docker 部署指南](DOCKER_GUIDE.md)
- [4GB 优化配置](../examples/docker/docker-compose.4gb-optimized.yml)
- [Dockerfile 优化对比](DOCKERFILE_OPTIMIZATION_COMPARISON.md)

---

## 🔄 更新日志

### 2026-02-05

- ✅ 完成镜像优化（-38% 体积）
- ✅ 在 GTX 1050 Ti 上测试优化镜像
- ✅ 实现 FP16 半精度代码
- ✅ 实现 TTS 文本分块代码
- ✅ 创建完整优化文档
- ⏳ 等待重新构建镜像进行 FP16 和分块测试

---

**测试负责人**: OpenCode AI  
**最后更新**: 2026-02-05 18:45 CST
