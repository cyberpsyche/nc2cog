# nc2cog 使用示例

## 基础用法

### 转换单个文件
```bash
nc2cog input.nc output/
```

### 指定输出文件名
```bash
nc2cog input.nc output/my_custom_name.tif
```

### 转换整个目录
```bash
nc2cog input_dir/ output/
```

## 多维 NetCDF 文件转换

当输入文件包含多个变量和时间维度（如 `PRE(time, lat, lon)`, `REF(time, lat, lon)`）时，工具会自动检测并将其转换为多波段 COG 文件，每个变量一个文件，时间步作为波段。

### 自动发现所有变量
```bash
nc2cog MPF_V4_20251113144500.nc output/
# 输出: output/PRE.tif (10 bands), output/REF.tif (10 bands)
```

### 指定转换特定变量
```bash
# 仅转换 PRE 变量（输出到目录）
nc2cog --variables PRE MPF_V4_20251113144500.nc output/

# 转换多个变量（输出到目录）
nc2cog --variables PRE,REF MPF_V4_20251113144500.nc output/

# 转换单个变量到指定文件
nc2cog --variables PRE MPF_V4_20251113144500.nc output/MPF_v4_PRE.tif
```

### 输出文件结构
每个输出的 COG 文件包含：
- **波段 1**: `time=0, 2025-11-13T06:30:00`
- **波段 2**: `time=1, 2025-11-13T07:30:00`
- **...**
- **波段 N**: `time=N-1, YYYY-MM-DDTHH:MM:SS`

### 预览多维转换（dry-run）
```bash
# 目录模式预览
nc2cog --dry-run MPF_V4_20251113144500.nc output/
# 输出示例:
# Multi-dimensional mode: converting variables: PRE, REF
#   PRE -> output/PRE.tif
#   REF -> output/REF.tif

# 文件模式预览
nc2cog --dry-run --variables PRE MPF_V4_20251113144500.nc output/MPF_v4_PRE.tif
# 输出示例:
# Multi-dimensional mode: converting variables: PRE
#   Output: output/MPF_v4_PRE.tif (variable: PRE)
```

## 压缩选项

### 高压缩比设置
```bash
# 使用最高压缩级别
nc2cog input.nc output/ --compression deflate --zlevel 9
```

### 不同压缩算法
```bash
# 使用 LZW 压缩
nc2cog input.nc output/ --compression lzw

# 使用 JPEG 压缩（适合影像数据）
nc2cog input.nc output/ --compression jpeg
```

## 性能调优

### 自定义瓦片和块大小
```bash
# 较大的瓦片和块尺寸（适合大文件访问）
nc2cog input.nc output/ --tile-size 1024 --block-size 512

# 较小的瓦片和块尺寸（适合小文件或内存受限环境）
nc2cog input.nc output/ --tile-size 256 --block-size 128
```

## 概览（金字塔）控制

### 概览重采样方法
```bash
# 最近邻（最快，适合分类数据）
nc2cog input.nc output/ --resampling nearest

# 双线性（平衡速度和质量）
nc2cog input.nc output/ --resampling bilinear

# 三次卷积（高质量，适合连续数据）
nc2cog input.nc output/ --resampling cubic

# 平均法（适合统计降采样）
nc2cog input.nc output/ --resampling average
```

### 概览层级控制
```bash
# 默认概览层级（适合大多数情况）
nc2cog input.nc output/ --overview-levels 2,4,8,16

# 更多层级（适合需要精细多尺度浏览的科学数据）
nc2cog input.nc output/ --overview-levels 2,4,8,16,32,64

# 较少层级（适合快速浏览）
nc2cog input.nc output/ --overview-levels 2,4
```

## 综合参数使用

### 高质量科学数据处理
```bash
# 高压缩比 + 高质量概览 + 适合科学数据
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --tile-size 512 \
  --block-size 256 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

### 多维文件 + 高级参数
```bash
# 转换多维 NC 文件并指定压缩和概览参数
nc2cog --variables PRE \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  MPF_V4_20251113144500.nc output/
```

### 快速预览处理
```bash
# 快速处理 + 适合快速浏览
nc2cog input.nc output/ \
  --compression lzw \
  --tile-size 1024 \
  --resampling bilinear \
  --overview-levels 2,4,8
```

### 大数据集并行处理
```bash
# 使用多个线程并行处理
nc2cog input_dir/ output/ \
  --threads 4 \
  --compression deflate \
  --zlevel 7 \
  --tile-size 512
```

## 与其他选项结合

### 干运行模式
```bash
# 预览将要执行的操作
nc2cog input.nc output/ --dry-run
```

### 恢复中断的处理
```bash
# 从中断处恢复处理（仅适用于批处理模式）
nc2cog input.nc output/ --resume
```

### 覆盖现有文件
```bash
# 强制覆盖已存在的输出文件
nc2cog input.nc output/ --overwrite
```

### 详细输出模式
```bash
# 显示详细的处理信息
nc2cog input.nc output/ --verbose
```

## 投影转换示例

### 基本重投影
```bash
# 将WGS84坐标系转换为Web Mercator投影
nc2cog input.nc output/ --src-proj EPSG:4326 --dst-proj EPSG:3857
```

### 自动检测源投影
```bash
# 指定目标投影，源投影从文件中自动检测
nc2cog input.nc output/ --dst-proj EPSG:3857
```

### 投影转换与其他参数结合
```bash
# 重投影结合高压缩比和高质量概览
nc2cog input.nc output/ \
  --src-proj EPSG:4326 \
  --dst-proj EPSG:3857 \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

### 气象数据重投影
```bash
# 将WGS84的气象数据转换为适用于Web发布的Web Mercator投影
nc2cog climate_data.nc output/ \
  --src-proj EPSG:4326 \
  --dst-proj EPSG:3857 \
  --compression deflate \
  --zlevel 8 \
  --resampling bilinear
```

### 海洋数据重投影
```bash
# 将海洋数据从WGS84转换为更适合极地地区的极地立体投影
nc2cog ocean_data.nc output/ \
  --src-proj EPSG:4326 \
  --dst-proj EPSG:3411 \
  --compression lzw \
  --resampling cubic
```

## 针对不同数据类型的建议配置

### 气象/气候数据
```bash
# 连续数值数据，需要高质量重采样
nc2cog climate_data.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

### 海洋数据
```bash
# 连续数据，可能需要较多层级
nc2cog ocean_data.nc output/ \
  --compression deflate \
  --zlevel 8 \
  --resampling bilinear \
  --overview-levels 2,4,8,16,32,64
```

### 土地利用分类数据
```bash
# 分类数据，需要保持类别完整性
nc2cog landuse_data.nc output/ \
  --compression deflate \
  --zlevel 6 \
  --resampling nearest \
  --overview-levels 2,4,8,16
```

### 遥感影像数据
```bash
# 影像数据，可能使用JPEG压缩
nc2cog imagery_data.nc output/ \
  --compression jpeg \
  --tile-size 1024 \
  --resampling average \
  --overview-levels 2,4,8
```

## 配置文件示例

创建 `config.yaml`:
```yaml
# 处理参数
compression: "deflate"
zlevel: 8
tile_size: [512, 512]
block_size: [256, 256]

# 投影参数（可选）
projection:
  source: "EPSG:4326"      # 源投影（可选，如果未指定则从输入文件自动检测）
  target: "EPSG:3857"      # 目标投影（必选，当需要重投影时）
  resampling_method: "bilinear"  # 重投影时使用的重采样方法

# 输出选项
overviews:
  resampling: "cubic"
  levels: [2, 4, 8, 16, 32]

# 处理控制
overwrite: false
skip_errors: true
```

使用配置文件：
```bash
nc2cog --config config.yaml input.nc output/
```

带有投影转换的配置文件使用：
```bash
nc2cog --config config_with_projection.yaml input.nc output/
```

## 最佳实践

1. **对于科学数据**：使用 deflate 压缩，高 zlevel，cubic 重采样
2. **对于影像数据**：考虑使用 jpeg 压缩，bilinear 重采样
3. **对于分类数据**：使用 nearest 重采样方法
4. **对于大数据集**：使用多线程并合理设置 tile-size 和 block-size
5. **对于小图像**：不需要过多的概览层级
6. **对于大图像**：可以设置更多层级以获得更好的多尺度浏览体验
7. **对于多维 NC 文件**：使用 `--dry-run` 预览将生成哪些输出文件
