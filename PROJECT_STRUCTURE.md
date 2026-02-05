# OpenTalker 项目结构

## 📁 目录结构

```
OpenTalker/
├── README.md                           # 项目主文档
├── AGENTS.md                           # AI 开发助手指南
├── LICENSE                             # Apache 2.0 许可证
├── pyproject.toml                      # Python 项目配置
├── docker-compose.yml                  # 主 Docker Compose 配置
├── Dockerfile                          # 单体应用 Dockerfile
├── .dockerignore                       # Docker 忽略文件
│
├── docs/                               # 📚 文档目录
│   ├── README.md                       # 文档索引
│   ├── DOCKER_IMAGES_GUIDE.md          # Docker 镜像使用指南
│   ├── DOCKER_GUIDE.md                 # Docker 部署指南
│   ├── README.workspace.md             # 微服务架构指南
│   ├── DOCKER_OPTIMIZATION.md          # 镜像优化方案
│   └── archive/                        # 归档文档
│
├── examples/                           # 📝 示例配置
│   └── docker/                         # Docker 示例
│       ├── README.md                   # Docker 示例说明
│       ├── docker-compose.ghcr.yml     # GHCR 镜像部署
│       ├── docker-compose.china.yml    # 国内镜像部署
│       └── docker-compose.workspace.yml # 微服务部署
│
├── scripts/                            # 🔧 工具脚本
│   ├── download_models.sh              # 模型下载脚本
│   ├── init_models.py                  # 模型初始化脚本
│   ├── build_docker.sh                 # Docker 构建脚本
│   └── deploy-workspace.sh             # 微服务部署脚本
│
├── gateway/                            # 🚪 API Gateway 服务
│   ├── app/                            # 应用代码
│   │   ├── main.py                     # FastAPI 应用入口
│   │   ├── routers/                    # 路由模块
│   │   ├── models.py                   # 数据模型
│   │   └── config.py                   # 配置管理
│   ├── Dockerfile                      # Gateway Dockerfile
│   ├── pyproject.toml                  # Gateway 依赖
│   └── tests/                          # 测试文件
│
├── stt-service/                        # 🎤 STT 服务
│   ├── app/                            # 应用代码
│   │   ├── main.py                     # FastAPI 应用入口
│   │   ├── service.py                  # STT 服务逻辑
│   │   ├── models.py                   # 数据模型
│   │   └── config.py                   # 配置管理
│   ├── Dockerfile                      # STT Dockerfile
│   ├── Dockerfile.optimized            # 优化版 Dockerfile
│   ├── pyproject.toml                  # STT 依赖
│   └── tests/                          # 测试文件
│
├── tts-service/                        # 🗣️ TTS 服务
│   ├── app/                            # 应用代码
│   │   ├── main.py                     # FastAPI 应用入口
│   │   ├── service.py                  # TTS 服务逻辑
│   │   ├── models.py                   # 数据模型
│   │   └── config.py                   # 配置管理
│   ├── Dockerfile                      # TTS Dockerfile
│   ├── Dockerfile.optimized            # 优化版 Dockerfile
│   ├── pyproject.toml                  # TTS 依赖
│   └── tests/                          # 测试文件
│
├── tests/                              # 🧪 集成测试
│   ├── test_api.py                     # API 测试
│   ├── test_stt.py                     # STT 测试
│   └── test_tts.py                     # TTS 测试
│
└── models/                             # 📦 模型缓存目录（运行时创建）
    ├── qwen3-asr/                      # Qwen3 ASR 模型
    └── qwen3-tts/                      # Qwen3 TTS 模型
```

## 📄 核心文件说明

### 根目录

| 文件 | 说明 |
|------|------|
| `README.md` | 项目主文档，包含快速开始、API 文档、配置说明 |
| `AGENTS.md` | AI 开发助手指南，包含构建、测试、代码规范 |
| `docker-compose.yml` | 主 Docker Compose 配置，单体应用部署 |
| `Dockerfile` | 单体应用 Dockerfile |
| `pyproject.toml` | Python 项目配置，依赖管理 |

### 文档目录 (docs/)

| 文件 | 说明 |
|------|------|
| `README.md` | 文档索引，快速导航 |
| `DOCKER_IMAGES_GUIDE.md` | Docker 镜像使用指南，包含 GHCR 和国内镜像源 |
| `DOCKER_GUIDE.md` | 完整的 Docker 部署指南 |
| `README.workspace.md` | 微服务架构部署指南 |
| `DOCKER_OPTIMIZATION.md` | 镜像优化方案，减小 37% 体积 |

### 示例目录 (examples/)

| 文件 | 说明 |
|------|------|
| `docker/docker-compose.ghcr.yml` | 使用 GHCR 公开镜像部署 |
| `docker/docker-compose.china.yml` | 使用国内镜像源部署（推荐国内用户） |
| `docker/docker-compose.workspace.yml` | 微服务架构部署 |

### 脚本目录 (scripts/)

| 文件 | 说明 |
|------|------|
| `download_models.sh` | 下载 Qwen3 模型 |
| `init_models.py` | 初始化和验证模型 |
| `build_docker.sh` | 构建所有 Docker 镜像 |
| `deploy-workspace.sh` | 部署微服务架构 |

### 服务目录

每个服务目录包含：
- `app/` - 应用代码
- `Dockerfile` - 标准 Dockerfile
- `Dockerfile.optimized` - 优化版 Dockerfile（STT/TTS）
- `pyproject.toml` - 服务依赖
- `tests/` - 单元测试

## 🚀 快速导航

### 我想...

#### 快速部署服务
→ 查看 [README.md](README.md#快速开始)

#### 使用 Docker 镜像部署
→ 查看 [docs/DOCKER_IMAGES_GUIDE.md](docs/DOCKER_IMAGES_GUIDE.md)

#### 在国内部署
→ 使用 [examples/docker/docker-compose.china.yml](examples/docker/docker-compose.china.yml)

#### 部署微服务架构
→ 查看 [docs/README.workspace.md](docs/README.workspace.md)

#### 构建 Docker 镜像
→ 运行 `./scripts/build_docker.sh`

#### 下载模型
→ 运行 `./scripts/download_models.sh`

#### 为 AI 助手配置环境
→ 查看 [AGENTS.md](AGENTS.md)

## 📦 Docker 镜像

### 公开镜像（GHCR）

| 服务 | 镜像地址 | 大小 |
|------|---------|------|
| Gateway | `ghcr.io/ddktoplabs/opentalker-gateway:v0.3.0` | 82.5MB |
| STT | `ghcr.io/ddktoplabs/opentalker-stt:v0.3.0` | 5.55GB |
| TTS | `ghcr.io/ddktoplabs/opentalker-tts:v0.3.0` | 5.49GB |

### 国内镜像源

| 服务 | 镜像地址 | 说明 |
|------|---------|------|
| Gateway | `ghcr.1ms.run/ddktoplabs/opentalker-gateway:v0.3.0` | 国内加速 |
| STT | `ghcr.1ms.run/ddktoplabs/opentalker-stt:v0.3.0` | 国内加速 |
| TTS | `ghcr.1ms.run/ddktoplabs/opentalker-tts:v0.3.0` | 国内加速 |

## 🔧 配置文件

### Docker Compose 配置

| 文件 | 用途 | 适用场景 |
|------|------|---------|
| `docker-compose.yml` | 单体应用部署 | 简单部署 |
| `examples/docker/docker-compose.ghcr.yml` | GHCR 镜像部署 | 国际用户 |
| `examples/docker/docker-compose.china.yml` | 国内镜像部署 | 国内用户 |
| `examples/docker/docker-compose.workspace.yml` | 微服务部署 | 开发环境 |

### Dockerfile

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 单体应用 Dockerfile |
| `gateway/Dockerfile` | Gateway 服务 Dockerfile |
| `stt-service/Dockerfile` | STT 服务 Dockerfile |
| `stt-service/Dockerfile.optimized` | STT 优化版（减小 37% 体积） |
| `tts-service/Dockerfile` | TTS 服务 Dockerfile |
| `tts-service/Dockerfile.optimized` | TTS 优化版（减小 37% 体积） |

## 📊 项目统计

- **代码行数**: ~5000 行
- **服务数量**: 3 个（Gateway, STT, TTS）
- **Docker 镜像**: 3 个公开镜像
- **文档数量**: 10+ 个
- **测试覆盖**: 单元测试 + 集成测试
- **支持的 GPU**: NVIDIA GTX 1050 Ti (4GB) 及以上

## 🔄 版本历史

- **v0.3.0** (2026-02-04)
  - ✅ 修复 Gateway TTS 语言映射问题
  - ✅ 添加 GHCR 公开镜像支持
  - ✅ 优化微服务架构
  - ✅ 完善文档结构
  - ✅ 添加国内镜像源支持

---

**最后更新**: 2026-02-05  
**版本**: v0.3.0  
**维护者**: DDKTopLabs
