# GitHub Actions 工作流文档

本项目使用 GitHub Actions 实现持续集成（CI）、Docker 镜像构建发布和依赖更新检查。

## 📋 工作流概览

| 工作流 | 文件 | 触发条件 | 用途 |
|--------|------|----------|------|
| CI | `.github/workflows/ci.yml` | Push/PR 到 main/develop | 代码质量检查、测试、Docker 构建验证 |
| Docker Build | `.github/workflows/docker.yml` | Push tag (v*) | 构建并发布 Docker 镜像 |
| Dependencies | `.github/workflows/dependencies.yml` | 每周一 / 手动触发 | 检查依赖更新、安全审计 |

## 🔄 CI 工作流

### 触发条件

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

### 任务说明

#### 1. 代码质量检查 (lint)

- **Ruff**: 代码风格和错误检查
- **Black**: 代码格式化检查
- **Mypy**: 类型检查（允许失败）

```bash
# 本地运行
source .venv/bin/activate
ruff check app/ tests/
black --check app/ tests/
mypy app/ --ignore-missing-imports
```

#### 2. 单元测试 (test)

- 使用 CPU-only PyTorch（CI 环境无 GPU）
- 跳过标记为 `@pytest.mark.gpu` 的测试
- 生成代码覆盖率报告
- 上传到 Codecov

```bash
# 本地运行（跳过 GPU 测试）
pytest tests/ -v -m "not gpu" --cov=app --cov-report=term-missing

# 本地运行（包含 GPU 测试）
pytest tests/ -v --cov=app --cov-report=term-missing
```

#### 3. Docker 构建测试 (docker-build)

- 验证 Dockerfile 可以成功构建
- 使用 BuildKit 缓存加速构建
- 不推送镜像（仅验证）

```bash
# 本地运行
docker build -t indextts-docker:test .
```

#### 4. 安全扫描 (security)

- 使用 Trivy 扫描文件系统漏洞
- 结果上传到 GitHub Security 标签

### 缓存策略

工作流使用以下缓存来加速构建：

1. **uv 依赖缓存**: `~/.cache/uv` 和 `.venv`
2. **Docker 层缓存**: `/tmp/.buildx-cache`

### 环境变量

```yaml
env:
  PYTHON_VERSION: "3.11"
  UV_VERSION: "0.1.0"
  CUDA_VISIBLE_DEVICES: ""  # 禁用 GPU
```

## 🐳 Docker 构建和发布工作流

### 触发条件

```yaml
on:
  push:
    tags:
      - 'v*'  # 例如: v1.0.0, v2.1.3
  workflow_dispatch:  # 手动触发
```

### 发布流程

1. **构建镜像**: 使用 Docker Buildx 构建 linux/amd64 镜像
2. **推送到 Docker Hub**: `yourusername/indextts-docker:tag`
3. **推送到 GHCR**: `ghcr.io/yourusername/indextts-docker:tag`
4. **创建 GitHub Release**: 自动生成发布说明
5. **更新 Docker Hub 描述**: 同步 README.md

### 镜像标签策略

```yaml
tags:
  - type=semver,pattern={{version}}      # v1.2.3 -> 1.2.3
  - type=semver,pattern={{major}}.{{minor}}  # v1.2.3 -> 1.2
  - type=semver,pattern={{major}}        # v1.2.3 -> 1
  - type=raw,value=latest                # latest
```

### 发布新版本

```bash
# 1. 创建并推送 tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 2. GitHub Actions 自动构建和发布

# 3. 验证镜像
docker pull yourusername/indextts-docker:1.0.0
docker pull ghcr.io/yourusername/indextts-docker:1.0.0
```

### 所需 Secrets

在 GitHub 仓库设置中配置以下 secrets：

| Secret | 用途 | 获取方式 |
|--------|------|----------|
| `DOCKER_USERNAME` | Docker Hub 用户名 | Docker Hub 账号 |
| `DOCKER_PASSWORD` | Docker Hub 密码/Token | Docker Hub -> Account Settings -> Security |
| `GITHUB_TOKEN` | GitHub API 访问 | 自动提供，无需配置 |

配置步骤：
1. 进入仓库 Settings -> Secrets and variables -> Actions
2. 点击 "New repository secret"
3. 添加上述 secrets

## 📦 依赖更新工作流

### 触发条件

```yaml
on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一 00:00 UTC (北京时间 08:00)
  workflow_dispatch:  # 手动触发
```

### 任务说明

#### 1. 检查依赖更新 (check-updates)

- 检查过期的 Python 包
- 更新依赖到最新版本
- 运行测试验证兼容性
- 自动创建 PR

```bash
# 本地检查过期包
source .venv/bin/activate
uv pip list --outdated

# 本地更新依赖
uv pip install --upgrade -e ".[dev]"
```

#### 2. 安全审计 (security-audit)

- 使用 `safety` 检查已知漏洞
- 使用 `pip-audit` 审计依赖
- 生成安全报告
- 发现漏洞时自动创建 Issue

```bash
# 本地运行安全审计
source .venv/bin/activate
uv pip install safety pip-audit
safety check
pip-audit
```

### 自动 PR 内容

依赖更新 PR 包含：

- 过期包列表
- 测试结果
- 审查清单
- 自动标签: `dependencies`, `automated`

### 手动触发

```bash
# 在 GitHub 网页上
Actions -> Dependency Updates -> Run workflow

# 或使用 GitHub CLI
gh workflow run dependencies.yml
```

## 🔧 本地开发工作流

### 设置开发环境

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 2. 创建虚拟环境
uv venv

# 3. 安装依赖
source .venv/bin/activate
uv pip install -e ".[dev]"

# 4. 安装 pre-commit hooks（可选）
pre-commit install
```

### 运行检查

```bash
# 代码格式化
black app/ tests/

# 代码检查
ruff check app/ tests/ --fix

# 类型检查
mypy app/

# 运行测试
pytest tests/ -v

# 运行测试（跳过 GPU）
pytest tests/ -v -m "not gpu"

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### 提交前检查清单

- [ ] 代码通过 `ruff check`
- [ ] 代码通过 `black --check`
- [ ] 测试通过 `pytest`
- [ ] 类型检查通过 `mypy`（可选）
- [ ] 更新文档（如有 API 变更）
- [ ] 添加测试（如有新功能）

## 📊 状态徽章

在 README.md 中添加以下徽章：

```markdown
[![CI](https://github.com/yourusername/indextts-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/indextts-docker/actions/workflows/ci.yml)
[![Docker Build](https://github.com/yourusername/indextts-docker/actions/workflows/docker.yml/badge.svg)](https://github.com/yourusername/indextts-docker/actions/workflows/docker.yml)
[![codecov](https://codecov.io/gh/yourusername/indextts-docker/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/indextts-docker)
```

替换 `yourusername` 为你的 GitHub 用户名。

## 🐛 故障排查

### CI 失败：依赖安装超时

**问题**: uv 安装依赖时超时

**解决方案**:
```yaml
# 在工作流中增加超时时间
- name: Install dependencies
  timeout-minutes: 30
  run: uv pip install -e ".[dev]"
```

### Docker 构建失败：缓存问题

**问题**: Docker 构建缓存损坏

**解决方案**:
```bash
# 清除 GitHub Actions 缓存
gh cache delete <cache-key>

# 或在工作流中禁用缓存
cache-from: type=gha
cache-to: type=gha,mode=max
```

### 测试失败：GPU 测试未跳过

**问题**: CI 尝试运行 GPU 测试

**解决方案**:
```python
# 确保测试标记正确
@pytest.mark.gpu
def test_gpu_function():
    pass

# 运行时跳过 GPU 测试
pytest -m "not gpu"
```

### Docker 推送失败：认证错误

**问题**: Docker Hub 认证失败

**解决方案**:
1. 检查 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD` secrets
2. 使用 Access Token 而不是密码
3. 验证 Token 权限包含 `Read, Write, Delete`

### 依赖更新 PR 创建失败

**问题**: 没有权限创建 PR

**解决方案**:
```yaml
# 确保工作流有正确的权限
permissions:
  contents: write
  pull-requests: write
```

## 🔐 安全最佳实践

1. **Secrets 管理**
   - 不要在代码中硬编码 secrets
   - 使用 GitHub Secrets 存储敏感信息
   - 定期轮换 tokens

2. **依赖安全**
   - 启用 Dependabot 安全更新
   - 定期运行安全审计
   - 及时更新有漏洞的依赖

3. **镜像安全**
   - 使用 Trivy 扫描镜像漏洞
   - 使用最小化基础镜像
   - 定期更新基础镜像

4. **权限最小化**
   - 只授予工作流必需的权限
   - 使用 `permissions` 限制 token 权限

## 📚 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [uv 文档](https://github.com/astral-sh/uv)
- [pytest 文档](https://docs.pytest.org/)
- [Trivy 文档](https://aquasecurity.github.io/trivy/)

## 🤝 贡献

如需改进工作流，请：

1. Fork 仓库
2. 创建特性分支
3. 修改工作流文件
4. 测试工作流
5. 提交 PR

---

**注意**: 首次使用前，请确保配置所有必需的 GitHub Secrets。
