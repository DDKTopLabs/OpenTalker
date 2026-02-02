# GitHub Actions 工作流创建完成

## ✅ 已创建的文件

### 工作流文件

1. **`.github/workflows/ci.yml`** - CI 工作流
   - 代码质量检查（Ruff, Black, Mypy）
   - 单元测试（pytest，跳过 GPU 测试）
   - Docker 构建验证
   - 安全扫描（Trivy）

2. **`.github/workflows/docker.yml`** - Docker 构建和发布
   - 构建 Docker 镜像
   - 推送到 Docker Hub 和 GHCR
   - 自动创建 GitHub Release
   - 更新 Docker Hub 描述

3. **`.github/workflows/dependencies.yml`** - 依赖更新检查
   - 每周检查依赖更新
   - 自动创建更新 PR
   - 安全审计（Safety, Pip-Audit）
   - 发现漏洞时创建 Issue

### 配置文件

4. **`.pre-commit-config.yaml`** - Pre-commit hooks
   - Ruff 代码检查
   - Black 格式化
   - Mypy 类型检查
   - 通用文件检查
   - Bandit 安全检查
   - Dockerfile 和 YAML 检查

5. **`.yamllint.yml`** - YAML 检查配置

6. **`pyproject.toml`** - 更新
   - 添加 pytest markers（gpu, slow）
   - 添加 bandit 配置

### 测试文件

7. **`tests/test_sample.py`** - 示例测试
   - 演示 GPU 测试标记用法
   - 提供测试模板

### 文档

8. **`.github/WORKFLOWS.md`** - 工作流详细文档
   - 工作流说明
   - 本地开发指南
   - 故障排查
   - 最佳实践

9. **`.github/SETUP.md`** - 设置指南
   - 快速设置步骤
   - Secrets 配置
   - 发布流程
   - 故障排查

10. **`README.md`** - 更新
    - 添加 CI 和 Docker 构建状态徽章

## 🎯 关键特性

### 1. 使用 uv 包管理器
- 快速依赖安装
- 自动使用清华镜像源
- 缓存优化

### 2. GPU 测试标记
```python
@pytest.mark.gpu
def test_gpu_function():
    # 在 CI 中自动跳过
    pass
```

运行测试：
```bash
# 跳过 GPU 测试（CI 环境）
pytest -m "not gpu"

# 运行所有测试（本地有 GPU）
pytest
```

### 3. 清华镜像源配置
- PyPI 镜像：`https://pypi.tuna.tsinghua.edu.cn/simple`
- PyTorch 镜像：`https://mirrors.tuna.tsinghua.edu.cn/pytorch/whl/cu121`
- HuggingFace 镜像：`https://hf-mirror.com`
- Ubuntu APT 镜像：自动配置

### 4. 多平台 Docker 镜像
- Docker Hub: `yourusername/indextts-docker`
- GHCR: `ghcr.io/yourusername/indextts-docker`
- 标签策略：`latest`, `1.0.0`, `1.0`, `1`

### 5. 自动化依赖管理
- 每周检查更新
- 自动创建 PR
- 安全审计
- 漏洞告警

## 📋 下一步操作

### 必需步骤

1. **配置 GitHub Secrets**
   ```
   DOCKER_USERNAME: 你的 Docker Hub 用户名
   DOCKER_PASSWORD: Docker Hub Access Token
   ```

2. **更新 README.md**
   - 将 `yourusername` 替换为你的 GitHub 用户名

3. **更新 docker.yml**
   - 将 `REGISTRY_IMAGE` 更新为你的 Docker Hub 仓库名

4. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "chore: add GitHub Actions workflows"
   git push origin main
   ```

### 可选步骤

5. **安装 pre-commit hooks**（本地开发）
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **配置 Codecov**（代码覆盖率）
   - 访问 https://codecov.io/
   - 添加仓库
   - 配置 `CODECOV_TOKEN` secret

7. **启用 Dependabot**
   - 创建 `.github/dependabot.yml`

8. **配置分支保护**
   - Settings -> Branches -> Add rule
   - 要求 CI 通过才能合并

## 🚀 发布第一个版本

```bash
# 1. 确保测试通过
pytest tests/ -v -m "not gpu"

# 2. 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 3. 推送标签
git push origin v1.0.0

# 4. GitHub Actions 自动构建和发布

# 5. 验证镜像
docker pull yourusername/indextts-docker:1.0.0
```

## 📊 工作流触发条件

| 工作流 | 触发条件 | 说明 |
|--------|----------|------|
| CI | Push/PR 到 main/develop | 自动运行 |
| Docker Build | Push tag (v*) | 发布版本时 |
| Dependencies | 每周一 00:00 UTC | 自动检查 |
| 所有工作流 | 手动触发 | Actions -> Run workflow |

## 🔧 本地开发命令

```bash
# 安装依赖
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 代码检查
ruff check app/ tests/ --fix
black app/ tests/
mypy app/

# 运行测试
pytest tests/ -v -m "not gpu"

# 运行测试（包含 GPU）
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# 安全检查
bandit -r app/
safety check
pip-audit

# Docker 构建
docker build -t indextts-docker:test .

# Pre-commit 检查
pre-commit run --all-files
```

## 📚 文档索引

- **快速设置**: `.github/SETUP.md`
- **工作流详解**: `.github/WORKFLOWS.md`
- **项目 README**: `README.md`
- **API 文档**: `README.md` 中的 API 文档部分

## 🎉 完成！

所有 GitHub Actions 工作流已创建完成。按照上述步骤配置后，你的项目将拥有：

- ✅ 自动化 CI/CD 流程
- ✅ 代码质量保证
- ✅ 自动化 Docker 镜像发布
- ✅ 依赖安全管理
- ✅ 完整的测试覆盖
- ✅ 清华镜像源优化

如有问题，请查看 `.github/SETUP.md` 中的故障排查部分。

---

**提示**: 记得将所有 `yourusername` 替换为你的实际 GitHub 用户名！
