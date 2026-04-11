# nc2cog - netCDF to Cloud-Optimized GeoTIFF Converter

## 简介

nc2cog 是一个专门用于将 netCDF 文件转换为 Cloud-Optimized GeoTIFF (COG) 格式的工具。该工具旨在优化大型科学数据集（特别是气象、气候和海洋数据）的处理，使其适合云端存储和高效访问。

## 特性

- **netCDF 转 COG**：将单个或批量的 netCDF 文件转换为 COG 格式
- **GDAL 兼容**：充分利用 GDAL 库的强大功能
- **高性能**：支持多线程处理和并行转换
- **高级压缩**：支持多种压缩算法和压缩级别
- **概览生成**：智能生成多级概览（金字塔）用于多尺度访问
- **GDAL 优化**：消除转换过程中的 GDAL 警告信息
- **灵活配置**：支持命令行参数和配置文件双重配置方式

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd nc2cog

# 安装依赖
pip install -r requirements.txt

# 安装 GDAL (必要)
# macOS: brew install gdal
# Linux: apt-get install gdal-bin libgdal-dev
# Windows: 通过 OSGeo4W 安装
```

## 快速开始

### 基本用法

```bash
# 转换单个 netCDF 文件
nc2cog input.nc output/

# 转换目录中的所有 netCDF 文件
nc2cog input_dir/ output/
```

### 高级用法

```bash
# 指定压缩类型和级别
nc2cog input.nc output/ --compression deflate --zlevel 9

# 设置性能相关参数
nc2cog input.nc output/ --tile-size 1024 --block-size 512

# 控制概览（金字塔）生成
nc2cog input.nc output/ --resampling cubic --overview-levels 2,4,8,16

# 组合使用多个参数
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 8 \
  --tile-size 1024 \
  --block-size 512 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32

# 并行处理
nc2cog input_dir/ output/ --threads 4

# 验证但不实际转换（dry-run）
nc2cog input.nc output/ --dry-run

# 恢复中断的转换
nc2cog input.nc output/ --resume
```

## 命令行参数详解

### 主要参数
- `input_path`: 输入文件路径（文件或目录）
- `output_path`: 输出目录路径

### 配置参数
- `--config, -c`: 指定配置文件路径

### 压缩相关
- `--compression`: 压缩类型（deflate, lzw, jpeg），默认: deflate
- `--zlevel`: 压缩级别（1-9），仅对 deflate 有效，默认: 6

### 性能相关
- `--tile-size`: COG 瓦片大小，默认: 512
- `--block-size`: 压缩块大小，默认: 256

### 概览控制
- `--resampling`: 概览重采样方法（nearest, bilinear, cubic, average, mode, gauss, rms），默认: nearest
- `--overview-levels`: 概览层级（逗号分隔），默认: 2,4,8,16

### 其他选项
- `--overwrite`: 覆盖现有输出文件
- `--dry-run`: 预演模式，显示将要处理的内容但不实际执行
- `--verbose, -v`: 详细输出模式
- `--resume`: 从中断处恢复
- `--threads`: 并行处理线程数，默认: 1

## 参数详细说明

### --resampling 概览重采样方法
- `nearest`: 最邻近法，速度快，适合分类数据
- `bilinear`: 双线性插值，平衡质量和速度
- `cubic`: 三次卷积，高质量，适合连续数据
- `average`: 平均法，适合降采样统计
- `mode`: 众数法，适合分类数据
- `gauss`: 高斯重采样，平滑效果好
- `rms`: 均方根重采样，适合特殊分析

### --overview-levels 概览层级
指定概览金字塔的缩小比例，例如：
- `2,4,8,16`: 生成缩小 2、4、8、16 倍的概览层级
- 每个数字表示分辨率缩小的倍数

**重要说明**：GDAL 会根据原始图像尺寸智能决定实际生成的概览层级。对于较小的图像，某些高层级可能不会被生成，以避免生成过小且无用的概览。

## 概览层级工作机制

1. **指定 vs 实际生成**：虽然您可以在命令行指定概览层级，但 GDAL 会根据原始图像尺寸智能判断哪些层级是实用的。

2. **智能优化**：对于 1781x1572 的图像：
   - 指定: `2,4,8,16,32`
   - 实际生成: `2,4` (即 890x786 和 445x393)
   - 原因: 更小的概览（如 55x49）被认为没有实用价值

3. **层级数量计算**：
   - 指定概览层级: 5 个 (2,4,8,16,32)
   - 实际概览层级: 2 个 (取决于图像尺寸)
   - 总可访问层级: 3 个 (原始 + 2 个概览)

## 配置文件示例

创建 `config.yaml`:

```yaml
# 处理参数
compression: "deflate"
zlevel: 6
tile_size: [512, 512]
block_size: [256, 256]

# 输出选项
overviews:
  resampling: "nearest"
  levels: [2, 4, 8, 16]

# 处理控制
overwrite: false
skip_errors: true
```

使用配置文件：
```bash
nc2cog --config config.yaml input.nc output/
```

## 错误处理和优化

### GDAL 警告消除
项目已优化以消除常见的 GDAL 警告：
- 为不同 GDAL 驱动使用正确的参数（GeoTIFF vs COG）
- 移除不兼容的参数选项
- 确保参数值在有效范围内

### 内存管理
- 使用临时文件避免内存溢出
- 支持大文件处理
- 自动内存清理

## 使用场景

### 科学数据
```bash
# 高压缩比，适合长期存储
nc2cog input.nc output/ --compression deflate --zlevel 9 --resampling cubic
```

### 快速访问
```bash
# 较小压缩比，快速读取
nc2cog input.nc output/ --compression lzw --tile-size 1024 --overview-levels 2,4
```

### Web 发布
```bash
# 优化的概览用于 Web GIS
nc2cog input.nc output/ --resampling bilinear --overview-levels 2,4,8,16,32
```

## 故障排除

### 常见问题
1. **GDAL 相关错误**: 确保正确安装了 GDAL 及其 Python 绑定
2. **权限错误**: 确保有输出目录的写入权限
3. **内存不足**: 对于大文件，考虑减少线程数或增加虚拟内存

### 性能优化
- 调整 `--tile-size` 和 `--block-size` 以获得最佳性能
- 根据原始图像大小选择合适的概览层级
- 使用 `--threads` 参数进行并行处理

## 技术说明

- **架构**: Python + GDAL
- **输出格式**: Cloud-Optimized GeoTIFF (COG)
- **处理流程**: netCDF → 中间 GeoTIFF → COG
- **概览生成**: 使用 GDAL BuildOverviews 方法
- **压缩**: 支持多种 GDAL 压缩算法