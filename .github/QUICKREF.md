# GitHub Actions 快速参考

## 🚀 常用命令

### 本地开发

```bash
# 安装依赖
uv pip install -e ".[dev]"

# 代码检查
ruff check app/ tests/ --fix
black app/ tests/

# 运行测试（跳过 GPU）
pytest -m "not gpu"

# 运行所有测试
pytest

# 构建 Docker
docker build -t test .
```

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 创建 PR（在 GitHub 网页上）

# 发布版本
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

## 📋 工作流状态

查看工作流状态：https://github.com/yourusername/indextts-docker/actions

## 🔑 必需的 Secrets

| Secret | 获取方式 |
|--------|----------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub -> Settings -> Security -> New Access Token |

## 🏷️ 版本标签规范

```bash
v1.0.0    # 主版本.次版本.修订版本
v1.0.0-rc.1  # 候选版本
v1.0.0-beta.1  # 测试版本
```

## 🧪 测试标记

```python
# 标记 GPU 测试
@pytest.mark.gpu
def test_gpu_function():
    pass

# 标记慢速测试
@pytest.mark.slow
def test_slow_function():
    pass

# 运行时跳过
pytest -m "not gpu"
pytest -m "not slow"
pytest -m "not gpu and not slow"
```

## 🐳 Docker 镜像

```bash
# Docker Hub
docker pull yourusername/indextts-docker:latest
docker pull yourusername/indextts-docker:1.0.0

# GitHub Container Registry
docker pull ghcr.io/yourusername/indextts-docker:latest
docker pull ghcr.io/yourusername/indextts-docker:1.0.0
```

## 📊 徽章

```markdown
[![CI](https://github.com/yourusername/indextts-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/indextts-docker/actions/workflows/ci.yml)
[![Docker](https://github.com/yourusername/indextts-docker/actions/workflows/docker.yml/badge.svg)](https://github.com/yourusername/indextts-docker/actions/workflows/docker.yml)
```

## 🔧 故障排查

| 问题 | 解决方案 |
|------|----------|
| CI 失败 | 查看 Actions 日志 |
| Docker 认证失败 | 检查 Secrets 配置 |
| 测试失败 | 本地运行 `pytest -v` |
| 依赖安装失败 | 检查 `pyproject.toml` |

## 📚 文档

- 设置指南: `.github/SETUP.md`
- 工作流详解: `.github/WORKFLOWS.md`
- 完整总结: `.github/SUMMARY.md`

## 🎯 检查清单

### 首次设置
- [ ] 配置 `DOCKER_USERNAME` secret
- [ ] 配置 `DOCKER_PASSWORD` secret
- [ ] 更新 README.md 中的用户名
- [ ] 更新 docker.yml 中的镜像名
- [ ] 推送代码到 GitHub
- [ ] 验证 CI 通过

### 发布版本
- [ ] 本地测试通过
- [ ] 代码检查通过
- [ ] 更新 CHANGELOG
- [ ] 创建版本标签
- [ ] 推送标签
- [ ] 验证 Docker 镜像
- [ ] 检查 GitHub Release

---

**快速链接**: [Setup](.github/SETUP.md) | [Workflows](.github/WORKFLOWS.md) | [Summary](.github/SUMMARY.md)
