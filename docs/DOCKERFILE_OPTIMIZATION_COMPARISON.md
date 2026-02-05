# Dockerfile 优化方案对比

## 问题分析

在 `pyproject.toml` 中我们已经配置了清华镜像源：

```toml
# PyPI 镜像（清华大学）
[[tool.uv.index]]
name = "tsinghua-pypi"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true

# PyTorch 镜像（官方 - CUDA 12.1 版本）
[[tool.uv.index]]
name = "pytorch-cu121"
url = "https://download.pytorch.org/whl/cu121"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu121" }
torchaudio = { index = "pytorch-cu121" }
```

但在 `Dockerfile.optimized` 中，我们使用了 `--index-url` 参数，这会**覆盖** `pyproject.toml` 中的配置。

## 方案对比

### ❌ 旧方案（Dockerfile.optimized）

```dockerfile
# 复制 pyproject.toml
COPY pyproject.toml .

# 手动指定索引，覆盖了 pyproject.toml 中的配置
RUN uv pip install --system --no-cache \
    torch>=2.1.0 torchaudio>=2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121

RUN uv pip install --system --no-cache \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    ... \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**问题**：
1. 重复配置索引源（pyproject.toml 和 Dockerfile 都有）
2. 维护困难：修改索引需要改两个地方
3. 容易出错：可能忘记更新某个地方
4. 违反 DRY 原则（Don't Repeat Yourself）

### ✅ 新方案（Dockerfile.optimized.v2）

```dockerfile
# 复制 pyproject.toml 和 app 代码
COPY pyproject.toml .
COPY app/ ./app/

# 使用 -e . 安装，自动读取 pyproject.toml 中的所有配置
RUN uv pip install --system --no-cache -e .
```

**优势**：
1. ✅ 单一配置源：只在 `pyproject.toml` 中配置
2. ✅ 自动使用清华镜像源
3. ✅ 自动使用 PyTorch CUDA 镜像
4. ✅ 维护简单：只需修改 `pyproject.toml`
5. ✅ 代码更简洁：一条命令安装所有依赖

## 工作原理

当执行 `uv pip install -e .` 时，uv 会：

1. 读取 `pyproject.toml` 中的 `[project.dependencies]`
2. 读取 `[[tool.uv.index]]` 配置的索引源
3. 读取 `[tool.uv.sources]` 配置的特定包索引
4. 自动从正确的索引下载对应的包：
   - `torch`, `torchaudio` → `https://download.pytorch.org/whl/cu121`
   - 其他包 → `https://pypi.tuna.tsinghua.edu.cn/simple`

## 镜像大小对比

两种方案的镜像大小相同，因为安装的包是一样的：

| 方案 | 镜像大小 | 说明 |
|------|---------|------|
| 旧方案 | 3.44GB | 手动指定索引 |
| 新方案 | 3.44GB | 自动读取配置 |

## 构建时间对比

新方案可能稍快，因为：
- 减少了一次 RUN 命令（Docker 层更少）
- uv 可以更好地优化依赖解析

## 推荐

**强烈推荐使用新方案（Dockerfile.optimized.v2）**，原因：
1. 更符合最佳实践
2. 维护更简单
3. 不容易出错
4. 代码更简洁

## 迁移步骤

1. 备份当前的 Dockerfile.optimized
2. 使用 Dockerfile.optimized.v2 替换
3. 测试构建：
   ```bash
   docker build -f Dockerfile.optimized.v2 -t test:latest .
   ```
4. 验证镜像功能正常
5. 更新 CI/CD 配置

## 注意事项

使用新方案时，需要确保：
1. `pyproject.toml` 中的 `[tool.hatch.build.targets.wheel]` 配置正确：
   ```toml
   [tool.hatch.build.targets.wheel]
   packages = ["app"]
   ```
2. 在 `COPY` 时需要同时复制 `pyproject.toml` 和 `app/` 目录
3. 使用 `-e` 标志（editable install）可以让 Python 直接引用 `/app` 目录

## 相关文档

- [uv 文档 - 索引配置](https://github.com/astral-sh/uv#index-configuration)
- [pyproject.toml 规范](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
