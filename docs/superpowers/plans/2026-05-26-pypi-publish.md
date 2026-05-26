# nc2cog PyPI 包迁移实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 nc2cog 从 `setup.py` + `requirements.txt` 迁移到 `pyproject.toml` + `uv` 构建系统，准备发布到 PyPI。

**Architecture:** 创建标准 `pyproject.toml` 作为唯一构建配置源（setuptools 后端），修改 `__version__.py` 使用 `importlib.metadata` 动态读取版本号，删除旧的 `setup.py` 和 `requirements.txt`，最后通过 `uv build` 验证构建产物。

**Tech Stack:** uv, setuptools, pyproject.toml, importlib.metadata, Python 3.9+

---

### Task 1: 创建 pyproject.toml

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: 创建 pyproject.toml**

在项目根目录创建 `pyproject.toml`，内容如下：

```toml
[project]
name = "nc2cog"
version = "0.1.3"
description = "Convert netCDF files to Cloud-Optimized GeoTIFF format with advanced compression"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [
    {name = "Sam Chen"}
]
keywords = ["netcdf", "cog", "geotiff", "gdal", "geospatial"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering :: GIS",
]

dependencies = [
    "GDAL>=3.8.0",
    "click>=8.1.0",
    "PyYAML>=6.0",
    "netCDF4>=1.6.0",
    "numpy>=1.21.0",
]

[project.urls]
Homepage = "https://github.com/cyberpsyche/nc2cog"
Repository = "https://github.com/cyberpsyche/nc2cog"

[project.scripts]
nc2cog = "nc2cog.cli:main"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

- [ ] **Step 2: 验证 pyproject.toml 语法**

```bash
uv pip compile pyproject.toml --dry-run 2>&1 | head -5
```

Expected: 不应报语法错误。如果 `uv` 未安装，先运行 `uv pip install uv`。

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml for uv-based build system"
```

---

### Task 2: 修改 `__version__.py` 使用 importlib.metadata

**Files:**
- Modify: `src/nc2cog/__version__.py`

- [ ] **Step 1: 重写 `__version__.py`**

将当前硬编码的版本号替换为动态读取：

**修改前 (`src/nc2cog/__version__.py`)：**
```python
__version__ = "0.1.2"
```

**修改后 (`src/nc2cog/__version__.py`)：**
```python
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nc2cog")
except PackageNotFoundError:
    __version__ = "unknown"
```

注意：`cli.py` 第 14 行通过 `from .__version__ import __version__` 导入此变量，第 18 行通过 `@click.version_option(version=__version__)` 使用它。修改后该导入路径仍然有效。

- [ ] **Step 2: 验证语法**

```bash
python -c "import ast; ast.parse(open('src/nc2cog/__version__.py').read()); print('Syntax OK')"
```

Expected: 输出 `Syntax OK`

- [ ] **Step 3: Commit**

```bash
git add src/nc2cog/__version__.py
git commit -m "refactor: read version from importlib.metadata instead of hardcoded"
```

---

### Task 3: 更新 .gitignore 并删除旧构建文件

**Files:**
- Modify: `.gitignore`
- Delete: `setup.py`
- Delete: `requirements.txt`

- [ ] **Step 1: 在 .gitignore 末尾添加 uv.lock 忽略**

在 `.gitignore` 文件末尾追加以下内容（因为这是一个库项目，不需要向终端用户提交锁定文件）：

```
# uv (library project - don't commit lock file)
uv.lock
```

- [ ] **Step 2: 删除 setup.py**

```bash
rm setup.py
```

- [ ] **Step 3: 删除 requirements.txt**

```bash
rm requirements.txt
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore setup.py requirements.txt
git commit -m "chore: remove setup.py and requirements.txt, add uv.lock to gitignore"
```

---

### Task 4: 构建验证

**Files:**
- No file changes — build verification only

- [ ] **Step 1: 安装 uv（如未安装）**

```bash
which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
```

Expected: 输出 uv 的安装路径或安装成功信息。

- [ ] **Step 2: 执行构建**

```bash
uv build
```

Expected: 输出类似以下内容：
```
Building source distribution...
Building wheel from source distribution...
Successfully built dist/nc2cog-0.1.3.tar.gz
Successfully built dist/nc2cog-0.1.3-py3-none-any.whl
```

- [ ] **Step 3: 验证 wheel 内容**

```bash
unzip -l dist/nc2cog-0.1.3-py3-none-any.whl | head -20
```

Expected: 应包含 `nc2cog/__init__.py`、`nc2cog/cli.py`、`nc2cog/__version__.py` 等包内文件，以及 `nc2cog-0.1.3.dist-info/METADATA`。

- [ ] **Step 4: 验证 METADATA 中的版本号**

```bash
unzip -p dist/nc2cog-0.1.3-py3-none-any.whl nc2cog-0.1.3.dist-info/METADATA | grep "^Version:"
```

Expected: 输出 `Version: 0.1.3`

- [ ] **Step 5: 验证 METADATA 中的 entry points**

```bash
unzip -p dist/nc2cog-0.1.3-py3-none-any.whl nc2cog-0.1.3.dist-info/METADATA | grep -A2 "console_scripts"
```

Expected: 应包含 `nc2cog = nc2cog.cli:main`

- [ ] **Step 6: Commit 构建产物验证通过（不提交 dist/，仅确认）**

构建产物 `dist/` 已在 `.gitignore` 中，不需要提交。此任务仅验证构建成功。

---

### Task 5: 发布到 PyPI（可选，需要 PyPI token）

**Files:**
- No file changes — release only

- [ ] **Step 1: 确认 PyPI 凭证**

发布需要 PyPI API token。可以通过以下方式之一提供：

```bash
# 方式一：环境变量
export UV_PUBLISH_TOKEN="pypi-xxxxx"

# 方式二：交互式
# 直接运行 uv publish，会提示输入用户名和密码/token
```

- [ ] **Step 2: 发布到 TestPyPI（推荐先测试）**

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

Expected: 输出 `Published nc2cog 0.1.3` 或类似成功信息。

- [ ] **Step 3: 发布到正式 PyPI**

```bash
uv publish
```

Expected: 输出 `Published nc2cog 0.1.3` 或类似成功信息。

- [ ] **Step 4: 验证 PyPI 页面**

访问 https://pypi.org/project/nc2cog/ 确认：
- 版本号显示为 `0.1.3`
- 作者显示为 `Sam Chen`
- README 正确渲染
- 分类器正确显示

此任务不产生 git commit。
