# OpenTalker Workspace 测试指南

## 本地测试（开发环境）

### 1. 安装依赖

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 克隆项目
git clone https://github.com/DDKTopLabs/OpenTalker.git
cd OpenTalker

# 为每个服务安装依赖
cd stt-service && uv venv && source .venv/bin/activate && uv pip install -e . && deactivate && cd ..
cd tts-service && uv venv && source .venv/bin/activate && uv pip install -e . && deactivate && cd ..
cd gateway && uv venv && source .venv/bin/activate && uv pip install -e . && deactivate && cd ..
```

### 2. 启动服务（三个终端）

**终端 1 - STT 服务:**
```bash
cd stt-service
source .venv/bin/activate
export HF_ENDPOINT=https://hf-mirror.com
python -m app.main
```

**终端 2 - TTS 服务:**
```bash
cd tts-service
source .venv/bin/activate
export HF_ENDPOINT=https://hf-mirror.com
python -m app.main
```

**终端 3 - Gateway:**
```bash
cd gateway
source .venv/bin/activate
python -m app.main
```

### 3. 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 测试 STT（需要音频文件）
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@test_audio.wav" \
  -F "model=qwen3-asr"

# 测试 TTS
VOICE_BASE64=$(base64 -i test_audio.wav)
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"indextts-2\",\"input\":\"你好世界\",\"voice\":\"$VOICE_BASE64\"}" \
  --output output.wav
```

## Mac mini M4 部署测试

### 方式 1: 使用部署脚本（推荐）

```bash
# 在 Mac mini M4 上执行
curl -sSL https://raw.githubusercontent.com/DDKTopLabs/OpenTalker/main/scripts/deploy-workspace.sh | bash

# 启动服务
cd ~/OpenTalker-Workspace
./start-all.sh

# 查看日志
tail -f logs/gateway.log
tail -f logs/stt.log
tail -f logs/tts.log

# 测试
curl http://localhost:8000/health

# 停止服务
./stop-all.sh
```

### 方式 2: 手动部署

```bash
# SSH 到 Mac mini M4
ssh devocy@192.168.31.51

# 克隆项目
git clone https://github.com/DDKTopLabs/OpenTalker.git
cd OpenTalker

# 安装依赖（每个服务）
cd stt-service
uv venv
source .venv/bin/activate
uv pip install -e .
deactivate
cd ..

cd tts-service
uv venv
source .venv/bin/activate
uv pip install -e .
deactivate
cd ..

cd gateway
uv venv
source .venv/bin/activate
uv pip install -e .
deactivate
cd ..

# 启动服务（后台运行）
nohup ./stt-service/.venv/bin/python -m stt-service.app.main > stt.log 2>&1 &
nohup ./tts-service/.venv/bin/python -m tts-service.app.main > tts.log 2>&1 &
nohup ./gateway/.venv/bin/python -m gateway.app.main > gateway.log 2>&1 &

# 测试
curl http://localhost:8000/health
```

## 验证依赖隔离

### 检查 STT 服务的 transformers 版本

```bash
cd stt-service
source .venv/bin/activate
python -c "import transformers; print(f'transformers: {transformers.__version__}')"
# 期望输出: transformers: 4.57.6 或更高
deactivate
```

### 检查 TTS 服务的 transformers 版本

```bash
cd tts-service
source .venv/bin/activate
python -c "import transformers; print(f'transformers: {transformers.__version__}')"
# 期望输出: transformers: 4.46.x - 4.56.x
deactivate
```

### 验证两个服务都能正常导入

```bash
# STT 服务
cd stt-service
source .venv/bin/activate
python -c "import qwen_asr; print('✅ qwen-asr 导入成功')"
deactivate

# TTS 服务
cd tts-service
source .venv/bin/activate
python -c "import indextts; print('✅ indextts 导入成功')"
deactivate
```

## 性能测试

### 并发测试

```bash
# 同时测试 STT 和 TTS
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@test1.wav" -F "model=qwen3-asr" &

curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"indextts-2","input":"测试","voice":"'$(base64 -i ref.wav)'"}' \
  --output out.wav &

wait
echo "✅ 并发测试完成"
```

### 响应时间测试

```bash
# STT 响应时间
time curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@test_audio.wav" -F "model=qwen3-asr"

# TTS 响应时间
time curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"indextts-2","input":"你好世界","voice":"'$(base64 -i test_audio.wav)'"}' \
  --output output.wav
```

## 故障排查

### 问题 1: 服务无法启动

```bash
# 检查端口占用
lsof -i :8000  # Gateway
lsof -i :8001  # STT
lsof -i :8002  # TTS

# 查看日志
tail -f logs/gateway.log
tail -f logs/stt.log
tail -f logs/tts.log
```

### 问题 2: 依赖安装失败

```bash
# 清理并重新安装
cd stt-service
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

## 成功标志

✅ 所有服务健康检查返回 "healthy"
✅ STT 能正确识别音频
✅ TTS 能生成音频文件
✅ Gateway 能正确代理请求
✅ 两个服务使用不同版本的 transformers
✅ 无依赖冲突错误
