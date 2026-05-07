# nc2cog 快速使用指南

## 简介
nc2cog 是一个专门用于将 netCDF 文件转换为 Cloud-Optimized GeoTIFF (COG) 格式的工具，具备先进的压缩和性能优化功能。

## 快速安装
```bash
# 安装 GDAL (必要)
# macOS: brew install gdal
# Ubuntu: sudo apt-get install gdal-bin libgdal-dev

# 安装 nc2cog
git clone <repository-url>
cd nc2cog
pip install -r requirements.txt
pip install -e .
```

## 基本使用
```bash
# 转换单个文件
nc2cog input.nc output/

# 指定输出文件名
nc2cog input.nc output/my_custom_name.tif

# 转换整个目录
nc2cog input_dir/ output/
```

## 多维 NetCDF 文件
```bash
# 自动检测并转换所有变量（输出到目录）
nc2cog MPF_V4_20251113144500.nc output/

# 指定转换特定变量（输出到目录）
nc2cog --variables PRE,REF MPF_V4_20251113144500.nc output/

# 指定转换单个变量到具体文件
nc2cog --variables PRE MPF_V4_20251113144500.nc output/MPF_v4_PRE.tif
```

## 常用参数
```bash
# 高压缩比
nc2cog input.nc output/ --compression deflate --zlevel 9

# 性能优化
nc2cog input.nc output/ --tile-size 1024 --block-size 512

# 概览控制
nc2cog input.nc output/ --resampling cubic --overview-levels 2,4,8,16
```

## 重要提示
- `--overview-levels` 指定的层级数不一定全部生成，GDAL会根据源图像大小智能决定
- 对于较小图像（如1781x1572），指定2,4,8,16,32可能只生成2,4层级
- 使用 `--dry-run` 参数预览将要执行的操作
- 多维文件需要安装 netCDF4 库（已在 requirements.txt 中）

## 示例组合
```bash
# 科学数据处理
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --tile-size 512 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32

# 多维文件 + 高质量参数
nc2cog --variables PRE \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32 \
  MPF_V4_20251113144500.nc output/

# 多维文件 + 指定输出文件
nc2cog --variables PRE \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32 \
  MPF_V4_20251113144500.nc output/MPF_v4_PRE.tif

# 并行处理大数据集
nc2cog input_dir/ output/ \
  --threads 4 \
  --compression deflate \
  --zlevel 7
```

## 完整文档
详见项目文档:
- [README.md](README.md) - 项目概览
- [INSTALLATION.md](INSTALLATION.md) - 安装指南
- [docs/user_guide.md](docs/user_guide.md) - 用户指南
- [docs/examples.md](docs/examples.md) - 使用示例
