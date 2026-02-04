#!/bin/bash
# OpenTalker Workspace 部署脚本
# 用于在 Mac mini M4 上部署微服务架构

set -e

echo "========================================="
echo "OpenTalker Workspace 部署脚本"
echo "========================================="

# 配置
REPO_URL="https://github.com/DDKTopLabs/OpenTalker.git"
INSTALL_DIR="$HOME/OpenTalker-Workspace"
HF_ENDPOINT="https://hf-mirror.com"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 检查 uv
info "检查 uv 安装..."
if ! command -v uv &> /dev/null; then
    warn "uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
info "✅ uv 版本: $(uv --version)"

# 2. 克隆或更新代码
if [ -d "$INSTALL_DIR" ]; then
    info "更新现有代码..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    info "克隆代码仓库..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 3. 设置环境变量
info "设置环境变量..."
export HF_ENDPOINT="$HF_ENDPOINT"
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"

# 4. 创建模型目录
info "创建模型目录..."
mkdir -p models/qwen3-asr models/indextts

# 5. 安装 STT 服务依赖
info "安装 STT 服务依赖..."
cd "$INSTALL_DIR/stt-service"
uv venv
source .venv/bin/activate
uv pip install -e .
deactivate

# 6. 安装 TTS 服务依赖
info "安装 TTS 服务依赖..."
cd "$INSTALL_DIR/tts-service"
uv venv
source .venv/bin/activate
uv pip install -e .
deactivate

# 7. 安装 Gateway 依赖
info "安装 Gateway 依赖..."
cd "$INSTALL_DIR/gateway"
uv venv
source .venv/bin/activate
uv pip install -e .
deactivate

# 8. 创建启动脚本
info "创建启动脚本..."

# STT 启动脚本
cat > "$INSTALL_DIR/start-stt.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/stt-service"
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"
export HF_ENDPOINT=https://hf-mirror.com
source .venv/bin/activate
python -m app.main
EOF
chmod +x "$INSTALL_DIR/start-stt.sh"

# TTS 启动脚本
cat > "$INSTALL_DIR/start-tts.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/tts-service"
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"
export HF_ENDPOINT=https://hf-mirror.com
source .venv/bin/activate
python -m app.main
EOF
chmod +x "$INSTALL_DIR/start-tts.sh"

# Gateway 启动脚本
cat > "$INSTALL_DIR/start-gateway.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/gateway"
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"
source .venv/bin/activate
python -m app.main
EOF
chmod +x "$INSTALL_DIR/start-gateway.sh"

# 统一启动脚本
cat > "$INSTALL_DIR/start-all.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "启动 OpenTalker Workspace..."

# 启动 STT 服务
echo "启动 STT 服务 (端口 8001)..."
nohup ./start-stt.sh > logs/stt.log 2>&1 &
echo $! > logs/stt.pid

sleep 3

# 启动 TTS 服务
echo "启动 TTS 服务 (端口 8002)..."
nohup ./start-tts.sh > logs/tts.log 2>&1 &
echo $! > logs/tts.pid

sleep 3

# 启动 Gateway
echo "启动 Gateway (端口 8000)..."
nohup ./start-gateway.sh > logs/gateway.log 2>&1 &
echo $! > logs/gateway.pid

echo "✅ 所有服务已启动"
echo ""
echo "查看日志:"
echo "  tail -f logs/stt.log"
echo "  tail -f logs/tts.log"
echo "  tail -f logs/gateway.log"
echo ""
echo "健康检查:"
echo "  curl http://localhost:8000/health"
EOF
chmod +x "$INSTALL_DIR/start-all.sh"

# 停止脚本
cat > "$INSTALL_DIR/stop-all.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "停止 OpenTalker Workspace..."

if [ -f logs/gateway.pid ]; then
    kill $(cat logs/gateway.pid) 2>/dev/null && echo "✅ Gateway 已停止"
    rm logs/gateway.pid
fi

if [ -f logs/stt.pid ]; then
    kill $(cat logs/stt.pid) 2>/dev/null && echo "✅ STT 服务已停止"
    rm logs/stt.pid
fi

if [ -f logs/tts.pid ]; then
    kill $(cat logs/tts.pid) 2>/dev/null && echo "✅ TTS 服务已停止"
    rm logs/tts.pid
fi

echo "所有服务已停止"
EOF
chmod +x "$INSTALL_DIR/stop-all.sh"

# 9. 创建日志目录
mkdir -p "$INSTALL_DIR/logs"

# 10. 完成
info "========================================="
info "✅ 部署完成！"
info "========================================="
echo ""
info "安装目录: $INSTALL_DIR"
echo ""
info "启动服务:"
echo "  cd $INSTALL_DIR"
echo "  ./start-all.sh"
echo ""
info "停止服务:"
echo "  ./stop-all.sh"
echo ""
info "查看日志:"
echo "  tail -f logs/gateway.log"
echo "  tail -f logs/stt.log"
echo "  tail -f logs/tts.log"
echo ""
info "健康检查:"
echo "  curl http://localhost:8000/health"
echo ""
warn "注意: 首次启动需要下载模型，可能需要较长时间"
