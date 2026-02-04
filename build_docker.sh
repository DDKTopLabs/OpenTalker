#!/bin/bash
# OpenTalker Docker 编译测试脚本

set -e

echo "========================================="
echo "  OpenTalker Docker 编译测试"
echo "========================================="
echo ""

# 检查Docker是否运行
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop或OrbStack"
    exit 1
fi

echo "✅ Docker运行正常"
echo ""

# 设置变量
REGISTRY="opentalker"
VERSION="v0.3.0"

# 编译Gateway
echo "========================================="
echo "1. 编译Gateway镜像"
echo "========================================="
cd gateway
docker build -t ${REGISTRY}/gateway:${VERSION} -t ${REGISTRY}/gateway:latest .
echo "✅ Gateway镜像编译完成"
echo ""
cd ..

# 编译STT Service
echo "========================================="
echo "2. 编译STT Service镜像"
echo "========================================="
cd stt-service
docker build -t ${REGISTRY}/stt-service:${VERSION} -t ${REGISTRY}/stt-service:latest .
echo "✅ STT Service镜像编译完成"
echo ""
cd ..

# 编译TTS Service
echo "========================================="
echo "3. 编译TTS Service镜像"
echo "========================================="
cd tts-service
docker build -t ${REGISTRY}/tts-service:${VERSION} -t ${REGISTRY}/tts-service:latest .
echo "✅ TTS Service镜像编译完成"
echo ""
cd ..

# 显示镜像列表
echo "========================================="
echo "编译完成的镜像"
echo "========================================="
docker images | grep opentalker

echo ""
echo "========================================="
echo "镜像大小统计"
echo "========================================="
echo "Gateway:     $(docker images ${REGISTRY}/gateway:latest --format '{{.Size}}')"
echo "STT Service: $(docker images ${REGISTRY}/stt-service:latest --format '{{.Size}}')"
echo "TTS Service: $(docker images ${REGISTRY}/tts-service:latest --format '{{.Size}}')"

echo ""
echo "========================================="
echo "✅ 所有镜像编译完成！"
echo "========================================="
echo ""
echo "使用以下命令启动服务:"
echo "  docker-compose -f docker-compose.workspace.yml up -d"
echo ""
echo "查看日志:"
echo "  docker-compose -f docker-compose.workspace.yml logs -f"
echo ""
echo "停止服务:"
echo "  docker-compose -f docker-compose.workspace.yml down"
