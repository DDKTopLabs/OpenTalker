# GitHub Actions 设置检查清单

使用此清单确保所有配置正确完成。

## ✅ 初始设置

### 1. GitHub Secrets 配置

- [ ] 访问 GitHub 仓库 Settings -> Secrets and variables -> Actions
- [ ] 创建 `DOCKER_USERNAME` secret
  - 值：你的 Docker Hub 用户名
- [ ] 创建 `DOCKER_PASSWORD` secret
  - 值：Docker Hub Access Token（不是密码！）
  - 获取方式：Docker Hub -> Account Settings -> Security -> New Access Token
  - 权限：Read, Write, Delete

### 2. 更新配置文件

- [ ] 编辑 `README.md`
  - 将所有 `yourusername` 替换为你的 GitHub 用户名
  - 检查徽章链接是否正确
  
- [ ] 编辑 `.github/workflows/docker.yml`
  - 更新 `REGISTRY_IMAGE` 为 `你的用户名/indextts-docker`
  
- [ ] 编辑 `.github/SETUP.md`（可选）
  - 将示例中的 `yourusername` 替换为你的用户名
  
- [ ] 编辑 `.github/WORKFLOWS.md`（可选）
  - 将示例中的 `yourusername` 替换为你的用户名

### 3. 推送到 GitHub

- [ ] 添加所有文件
  ```bash
  git add .
  ```

- [ ] 提交更改
  ```bash
  git commit -m "chore: add GitHub Actions workflows"
  ```

- [ ] 推送到 GitHub
  ```bash
  git push origin main
  ```

### 4. 验证 CI 工作流

- [ ] 访问 GitHub Actions 页面
  - URL: `https://github.com/你的用户名/indextts-docker/actions`
  
- [ ] 检查 CI 工作流是否运行
  - 应该看到 "CI" 工作流正在运行或已完成
  
- [ ] 查看工作流日志
  - 点击工作流查看详细日志
  - 确保所有任务都通过（绿色勾号）

- [ ] 如果失败，查看日志并修复问题
  - 常见问题：依赖安装失败、测试失败、Docker 构建失败

## ✅ 可选配置

### 5. Pre-commit Hooks（本地开发）

- [ ] 安装 pre-commit
  ```bash
  pip install pre-commit
  ```

- [ ] 安装 hooks
  ```bash
  pre-commit install
  ```

- [ ] 测试 hooks
  ```bash
  pre-commit run --all-files
  ```

### 6. Codecov（代码覆盖率）

- [ ] 访问 https://codecov.io/
- [ ] 使用 GitHub 账号登录
- [ ] 添加你的仓库
- [ ] 复制 Codecov token
- [ ] 在 GitHub Secrets 中添加 `CODECOV_TOKEN`
- [ ] 在 README.md 中添加 Codecov 徽章

### 7. Dependabot（依赖更新）

- [ ] 创建 `.github/dependabot.yml` 文件
- [ ] 配置更新策略
- [ ] 推送到 GitHub
- [ ] 验证 Dependabot 是否启用

### 8. 分支保护规则

- [ ] 访问 Settings -> Branches
- [ ] 点击 "Add rule"
- [ ] 配置 `main` 分支保护
  - [ ] Require a pull request before merging
  - [ ] Require status checks to pass before merging
  - [ ] 选择必需的检查：lint, test, docker-build
- [ ] 保存规则

## ✅ 发布第一个版本

### 9. 准备发布

- [ ] 确保所有测试通过
  ```bash
  pytest tests/ -v -m "not gpu"
  ```

- [ ] 确保代码检查通过
  ```bash
  ruff check app/ tests/
  black --check app/ tests/
  ```

- [ ] 更新版本号（如果需要）
  - 编辑 `pyproject.toml` 中的 `version`

- [ ] 创建 CHANGELOG.md（可选但推荐）
  - 记录版本变更

### 10. 创建版本标签

- [ ] 创建标签
  ```bash
  git tag -a v1.0.0 -m "Release version 1.0.0

  Features:
  - OpenAI-compatible STT API with Qwen3-ASR
  - OpenAI-compatible TTS API with IndexTTS2
  - GPU memory management for GTX 1050 Ti
  - Docker deployment with CUDA support
  - Tsinghua mirror optimization for China
  "
  ```

- [ ] 推送标签
  ```bash
  git push origin v1.0.0
  ```

### 11. 验证发布

- [ ] 访问 GitHub Actions
  - 检查 "Docker Build and Publish" 工作流是否运行
  
- [ ] 等待构建完成（可能需要 10-20 分钟）

- [ ] 检查 Docker Hub
  - 访问 `https://hub.docker.com/r/你的用户名/indextts-docker`
  - 确认镜像已发布
  - 检查标签：`latest`, `1.0.0`, `1.0`, `1`

- [ ] 检查 GitHub Container Registry
  - 访问 `https://github.com/你的用户名/indextts-docker/pkgs/container/indextts-docker`
  - 确认镜像已发布

- [ ] 检查 GitHub Release
  - 访问仓库的 Releases 页面
  - 确认 v1.0.0 release 已创建
  - 检查 release notes

### 12. 测试 Docker 镜像

- [ ] 拉取镜像
  ```bash
  docker pull 你的用户名/indextts-docker:1.0.0
  ```

- [ ] 运行镜像
  ```bash
  docker run -d --gpus all \
    -p 8000:8000 \
    -v ./models:/models \
    -e HF_ENDPOINT=https://hf-mirror.com \
    你的用户名/indextts-docker:1.0.0
  ```

- [ ] 测试 API
  ```bash
  curl http://localhost:8000/health
  ```

- [ ] 验证功能正常

## ✅ 持续维护

### 13. 定期检查

- [ ] 每周检查依赖更新 PR
  - 审查更新内容
  - 测试兼容性
  - 合并 PR

- [ ] 每月审查安全审计报告
  - 检查 Security 标签
  - 修复发现的漏洞

- [ ] 监控 CI 状态
  - 确保所有 PR 都通过 CI
  - 及时修复失败的构建

### 14. 性能优化

- [ ] 监控 GitHub Actions 使用量
  - Settings -> Billing
  - 确保在免费额度内

- [ ] 优化缓存策略
  - 检查缓存命中率
  - 清理过期缓存

- [ ] 优化构建时间
  - 并行运行独立任务
  - 使用更好的缓存策略

## 📊 完成度

- 初始设置: __ / 4
- 可选配置: __ / 4
- 发布版本: __ / 4
- 持续维护: __ / 2

**总计**: __ / 14

## 🎉 完成！

当所有检查项都完成后，你的 GitHub Actions 工作流就完全配置好了！

## 📚 参考文档

- 快速设置: `.github/SETUP.md`
- 工作流详解: `.github/WORKFLOWS.md`
- 完整总结: `.github/SUMMARY.md`
- 快速参考: `.github/QUICKREF.md`

## 🆘 需要帮助？

如果遇到问题：

1. 查看 `.github/SETUP.md` 中的故障排查部分
2. 查看 `.github/WORKFLOWS.md` 中的详细说明
3. 查看 GitHub Actions 日志
4. 在仓库中创建 Issue

---

**提示**: 可以打印此清单，逐项完成配置！
