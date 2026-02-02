# GitHub Actions 设置指南

本指南将帮助你为 `indextts-docker` 项目配置 GitHub Actions。

## 📋 前置要求

- GitHub 账号
- Docker Hub 账号（用于发布镜像）
- 项目已推送到 GitHub

## 🚀 快速设置

### 1. 配置 GitHub Secrets

进入你的 GitHub 仓库，按照以下步骤配置 secrets：

1. 点击 **Settings** 标签
2. 在左侧菜单中选择 **Secrets and variables** -> **Actions**
3. 点击 **New repository secret**
4. 添加以下 secrets：

#### 必需的 Secrets

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `DOCKER_USERNAME` | 你的 Docker Hub 用户名 | 例如: `johndoe` |
| `DOCKER_PASSWORD` | Docker Hub Access Token | 见下方获取方式 |

#### 获取 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击右上角头像 -> **Account Settings**
3. 选择 **Security** 标签
4. 点击 **New Access Token**
5. 输入描述（例如: `GitHub Actions`）
6. 选择权限: **Read, Write, Delete**
7. 点击 **Generate**
8. 复制生成的 token（只显示一次！）
9. 将 token 粘贴到 GitHub Secrets 的 `DOCKER_PASSWORD` 中

### 2. 更新 README.md 中的徽章

将 README.md 中的 `yourusername` 替换为你的 GitHub 用户名：

```bash
# 使用 sed 批量替换（macOS）
sed -i '' 's/yourusername/你的用户名/g' README.md

# 使用 sed 批量替换（Linux）
sed -i 's/yourusername/你的用户名/g' README.md
```

或手动编辑 README.md，替换以下内容：

```markdown
[![CI](https://github.com/yourusername/indextts-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/indextts-docker/actions/workflows/ci.yml)
```

改为：

```markdown
[![CI](https://github.com/你的用户名/indextts-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/你的用户名/indextts-docker/actions/workflows/ci.yml)
```

### 3. 更新 Docker 工作流中的镜像名称

编辑 `.github/workflows/docker.yml`，将 `REGISTRY_IMAGE` 更新为你的 Docker Hub 仓库：

```yaml
env:
  REGISTRY_IMAGE: 你的用户名/indextts-docker
```

### 4. 推送到 GitHub

```bash
git add .
git commit -m "chore: add GitHub Actions workflows"
git push origin main
```

### 5. 验证工作流

1. 进入 GitHub 仓库的 **Actions** 标签
2. 你应该看到 CI 工作流正在运行
3. 等待工作流完成（首次运行可能需要 5-10 分钟）

## 🔧 可选配置

### 启用 Codecov（代码覆盖率）

1. 访问 [Codecov](https://codecov.io/)
2. 使用 GitHub 账号登录
3. 添加你的仓库
4. 复制 Codecov token
5. 在 GitHub Secrets 中添加 `CODECOV_TOKEN`
6. 在 README.md 中添加徽章：

```markdown
[![codecov](https://codecov.io/gh/你的用户名/indextts-docker/branch/main/graph/badge.svg)](https://codecov.io/gh/你的用户名/indextts-docker)
```

### 启用 Dependabot

创建 `.github/dependabot.yml`：

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"

  # Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 配置分支保护规则

1. 进入 **Settings** -> **Branches**
2. 点击 **Add rule**
3. 在 **Branch name pattern** 中输入 `main`
4. 勾选以下选项：
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - 选择必需的状态检查：
     - `lint`
     - `test`
     - `docker-build`
5. 点击 **Create**

## 📦 发布第一个版本

### 1. 确保所有测试通过

```bash
# 本地运行测试
pytest tests/ -v -m "not gpu"

# 本地运行代码检查
ruff check app/ tests/
black --check app/ tests/
```

### 2. 创建版本标签

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0

Features:
- OpenAI-compatible STT API with Qwen3-ASR
- OpenAI-compatible TTS API with IndexTTS2
- GPU memory management for GTX 1050 Ti
- Docker deployment with CUDA support
- Tsinghua mirror optimization for China
"

# 推送标签
git push origin v1.0.0
```

### 3. 监控构建过程

1. 进入 **Actions** 标签
2. 查看 **Docker Build and Publish** 工作流
3. 等待构建完成（可能需要 10-20 分钟）

### 4. 验证发布

```bash
# 拉取镜像
docker pull 你的用户名/indextts-docker:1.0.0
docker pull 你的用户名/indextts-docker:latest

# 运行镜像
docker run -d --gpus all \
  -p 8000:8000 \
  -v ./models:/models \
  -e HF_ENDPOINT=https://hf-mirror.com \
  你的用户名/indextts-docker:1.0.0

# 测试 API
curl http://localhost:8000/health
```

### 5. 检查 GitHub Release

1. 进入仓库的 **Releases** 页面
2. 你应该看到自动创建的 v1.0.0 release
3. Release 包含 Docker 镜像的使用说明

## 🔍 故障排查

### CI 工作流失败

#### 问题：依赖安装失败

```
Error: Failed to install dependencies
```

**解决方案**：
1. 检查 `pyproject.toml` 语法是否正确
2. 确保所有依赖都可以从配置的镜像源获取
3. 查看详细日志确定具体失败的包

#### 问题：测试失败

```
Error: pytest failed
```

**解决方案**：
1. 本地运行测试确认问题：`pytest tests/ -v -m "not gpu"`
2. 检查是否有测试依赖 GPU（应该标记为 `@pytest.mark.gpu`）
3. 查看测试日志确定失败原因

#### 问题：Docker 构建失败

```
Error: failed to solve: process "/bin/sh -c ..." did not complete successfully
```

**解决方案**：
1. 本地构建测试：`docker build -t test .`
2. 检查 Dockerfile 语法
3. 确保所有 COPY 的文件存在

### Docker 发布工作流失败

#### 问题：Docker Hub 认证失败

```
Error: denied: requested access to the resource is denied
```

**解决方案**：
1. 验证 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD` secrets 是否正确
2. 确保使用的是 Access Token 而不是密码
3. 检查 Token 权限是否包含 Write 权限
4. 验证 Docker Hub 仓库名称是否正确

#### 问题：推送超时

```
Error: timeout waiting for push
```

**解决方案**：
1. 检查网络连接
2. 镜像可能太大，考虑优化 Dockerfile
3. 重新运行工作流

### 依赖更新工作流失败

#### 问题：无法创建 PR

```
Error: Resource not accessible by integration
```

**解决方案**：
1. 检查工作流权限：
```yaml
permissions:
  contents: write
  pull-requests: write
```
2. 确保 `GITHUB_TOKEN` 有足够权限

## 📊 监控和维护

### 定期检查

- **每周**：查看依赖更新 PR
- **每月**：审查安全审计报告
- **发布前**：确保所有 CI 检查通过

### 性能优化

1. **缓存优化**：
   - 监控缓存命中率
   - 定期清理过期缓存

2. **构建时间优化**：
   - 使用 Docker 层缓存
   - 并行运行独立任务

3. **成本控制**：
   - GitHub Actions 免费额度：2000 分钟/月（公开仓库无限）
   - 监控使用情况：Settings -> Billing

## 🎯 下一步

- [ ] 配置所有必需的 Secrets
- [ ] 更新 README.md 中的用户名
- [ ] 推送代码触发首次 CI 运行
- [ ] 创建第一个版本标签
- [ ] 验证 Docker 镜像发布成功
- [ ] 配置分支保护规则
- [ ] 启用 Dependabot（可选）
- [ ] 配置 Codecov（可选）

## 📚 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Hub 文档](https://docs.docker.com/docker-hub/)
- [工作流详细文档](.github/WORKFLOWS.md)

---

如有问题，请查看 [故障排查](#故障排查) 部分或提交 Issue。
