# PyPI 包发布设计：uv + setuptools 构建 nc2cog

**日期：** 2026-05-26
**状态：** 待审批

## 概述

将 nc2cog 项目从 `setup.py` + `requirements.txt` 迁移到 `pyproject.toml` 驱动的标准化结构，使用 `uv` 进行项目管理和构建，发布到 PyPI。

## 技术决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 构建系统 | `pyproject.toml` + setuptools 后端 | 最成熟稳定，GDAL 等 C 扩展依赖处理经验丰富 |
| 包管理器 | `uv` | 快速、现代，支持构建和发布一体化 |
| Python 版本 | `>=3.9` | 广泛支持，GDAL 兼容性好 |
| 版本管理 | 单一版本源在 `pyproject.toml` | 消除多处维护，`__version__.py` 通过 `importlib.metadata` 读取 |
| 项目布局 | 保留 `src/nc2cog/` | 无需变更现有代码结构 |

## 文件变更清单

### 新增文件
- **`pyproject.toml`**：包含所有构建元数据、依赖、入口点、分类器
- **`.python-version`**：声明项目使用 Python 3.9+（可选）

### 修改文件
- **`src/nc2cog/__version__.py`**：从硬编码版本改为 `importlib.metadata.version("nc2cog")`
- **`.gitignore`**：添加 `uv.lock` 忽略（库项目不需要锁定文件）

### 删除文件
- **`setup.py`**：功能收敛到 `pyproject.toml`
- **`requirements.txt`**：依赖已声明在 `pyproject.toml` 中

## pyproject.toml 核心配置

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

## 版本读取逻辑

`src/nc2cog/__version__.py`：
```python
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nc2cog")
except PackageNotFoundError:
    __version__ = "unknown"
```

## 构建和发布流程

1. `uv build` — 生成 sdist + wheel 到 `dist/`
2. `uv publish` — 上传到 PyPI（需 PyPI token）

## 风险和注意事项

- **GDAL 依赖**：GDAL 是 C 扩展库，在某些平台（Windows）可能需要预编译的 wheel。PyPI 上的 `GDAL` 包在 Python 3.9+ 上提供预编译 wheel，通常无需额外操作。
- **版本号**：首次发布应从 `0.1.3` 开始（当前代码版本为 `0.1.2`）。
- **README.md 链接**：`setup.py` 中的 `long_description` 使用相对路径读取 README，迁移到 `pyproject.toml` 后 `readme = "README.md"` 行为相同，确保 README 中的相对链接在 PyPI 上能正确渲染。
