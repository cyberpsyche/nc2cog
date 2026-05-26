# nc2cog - netCDF 转 COG TIFF 转换器

[English](README.md)

将 netCDF 文件转换为 Cloud-Optimized GeoTIFF (COG) 格式，支持高级压缩和性能优化设置。

## 🚀 特性

- **格式转换**：将 netCDF 文件转换为 Cloud-Optimized GeoTIFF (COG)
- **批量处理**：支持整个目录的 netCDF 文件批量转换
- **高级压缩**：支持 deflate、lzw、jpeg 压缩算法，可配置压缩级别
- **性能优化**：可配置的瓦片和块大小，优化读写性能
- **金字塔结构**：可自定义概览（金字塔）层级，支持多尺度访问
- **GDAL 优化**：消除 GDAL 警告，针对不同驱动优化参数
- **并行处理**：多线程转换，加速大批量处理
- **断点恢复**：支持中断后恢复转换
- **投影转换**：转换过程中支持坐标系重投影
- **灵活输出**：可输出到目录或直接输出到指定的 `.tif` 文件
- **丰富元数据**：自动向输出 COG 写入 18 个元数据字段（来源、范围、分辨率、最值、单位等）
- **清洁 COG 布局**：元数据在转换流水线中写入，不进行创建后的文件二次修改，不破坏 COG 布局优化

## 📋 环境要求

- Python 3.9+

## 🛠️ 安装

### 从 PyPI 安装（推荐）

```bash
pip install nc2cog
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/cyberpsyche/nc2cog.git
cd nc2cog

# 使用 uv 安装
uv pip install .

# 或使用 pip
pip install .
```

### 系统依赖

nc2cog 需要 GDAL 及 Python 绑定：

- **macOS**: `brew install gdal`
- **Ubuntu**: `sudo apt-get install gdal-bin libgdal-dev`
- **Windows**: 使用 OSGeo4W 安装器

## 🚀 快速开始

### 单文件转换

将单个 netCDF 文件转换为 COG TIFF：

```bash
nc2cog input.nc output/
```

指定输出文件名：

```bash
nc2cog input.nc output/my_custom_name.tif
```

### 批量转换

转换目录中的所有 netCDF 文件：

```bash
nc2cog input_dir/ output/
```

### 多维 NetCDF 文件

对于包含多个变量和时间维度的 netCDF 文件（如 `PRE(time, lat, lon)`、`REF(time, lat, lon)`），工具会自动检测文件结构，将每个变量转换为独立的多波段 COG 文件，时间步作为波段。

```bash
# 自动检测并转换所有变量
nc2cog MPF_V4_20251113144500.nc output/
# 输出: output/PRE.tif (N 波段), output/REF.tif (N 波段)

# 将指定变量转换到目录
nc2cog --variables PRE MPF_V4_20251113144500.nc output/

# 将单个变量转换到指定文件
nc2cog --variables PRE MPF_V4_20251113144500.nc output/MPF_v4_PRE.tif
# 输出: output/MPF_v4_PRE.tif (N 波段，每个波段对应一个时间步)
```

### 高级用法

自定义压缩和性能参数：

```bash
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --tile-size 1024 \
  --block-size 512 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32 \
  --metadata-source "My Satellite Data"
```

并行处理：

```bash
nc2cog input_dir/ output/ --threads 4
```

## ⚙️ 命令行参数

### 压缩参数
- `--compression` [deflate|lzw|jpeg]：选择压缩算法
- `--zlevel` [1-9]：设置 deflate 压缩级别（默认: 6）

### 性能参数
- `--tile-size` 整数：COG 瓦片大小（默认: 512）
- `--block-size` 整数：压缩块大小（默认: 256）

### 金字塔/概览参数
- `--resampling` [nearest|bilinear|cubic|...]：概览重采样方法（默认: nearest）
- `--overview-levels` 文本：概览层级（逗号分隔，默认: 2,4,8,16）

### 通用参数
- `--overwrite`：覆盖已有输出文件
- `--dry-run`：预览模式，显示将要处理的内容但不实际执行
- `--verbose`, `-v`：启用详细日志
- `--resume`：从中断处恢复
- `--threads` 整数：并行处理线程数（默认: 1）
- `--src-proj` 文本：源投影 EPSG 代码（如 EPSG:4326）
- `--dst-proj` 文本：目标投影 EPSG 代码（如 EPSG:3857）
- `--variables` 文本：指定要转换的变量名（逗号分隔，如 `PRE,REF`）。不指定时自动发现所有数据变量
- `--metadata-source` 文本：自定义 COG 元数据的来源名称。不指定时从 netCDF 全局属性（`source`、`platform`、`institution`）中自动检测
- `--version`, `-V`：显示版本信息并退出

## 📁 输出路径规则

`output_path` 参数的行为取决于其格式：

| 输出路径结尾 | 行为 |
|-------------|------|
| `.tif` | 直接输出到指定的文件 |
| `/` 或无扩展名 | 输出到目录（多维文件每变量一个文件） |

示例：
```bash
# 目录输出：生成 output/PRE.tif 和 output/REF.tif
nc2cog MPF_V4_20251113144500.nc output/

# 文件输出：生成指定的文件
nc2cog --variables PRE MPF_V4_20251113144500.nc output/MPF_v4_PRE.tif
```

**注意**：文件输出（`.tif` 结尾）仅适用于单变量转换。如果指定了多个变量但以 `.tif` 结尾，则只转换第一个变量到指定文件。

## 🔧 配置文件

对于复杂的转换需求，可以创建 `config.yaml` 配置文件：

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

# 元数据选项
metadata:
  source: ""        # 自定义来源名称（为空时从 netCDF 自动检测）
  offset: 0.0       # 数据偏移量
  scale: 1.0        # 数据缩放因子
  unit: ""          # 数据单位（为空时从 netCDF 自动检测）

# 处理控制
overwrite: false
skip_errors: true
```

使用方式：`nc2cog --config config.yaml input.nc output/`

## 📊 GDAL 优化

本工具通过使用适合不同驱动的参数来消除常见 GDAL 警告：

- **GTiff 驱动**：使用 `BLOCKXSIZE`/`BLOCKYSIZE` 而非 `TILEWIDTH`/`TILEHEIGHT`
- **COG 驱动**：使用 `BLOCKSIZE` 而非 `BLOCKXSIZE`/`BLOCKYSIZE`
- **概览处理**：优化避免 `COPY_SRC_OVERVIEWS` 冲突
- **清洁 COG 布局**：元数据在 COG 转换**之前**写入中间 GeoTIFF。GDAL COG 驱动自动将元数据从源文件携带到输出，无需在创建后二次修改文件，从而消除 "IFD has been rewritten" 警告

## 📋 COG 元数据

每个输出的 COG 文件包含 18 个在转换流水线中写入的元数据字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `Coordinate System` | 坐标系及投影信息 | `WGS84 (EPSG:4326)` |
| `Band Count` | 波段数（时间步数） | `10` |
| `Data Type` | 像素数据类型 | `Float32` |
| `Resolution` | 像素分辨率（度） | `0.01000000` |
| `Extent` | 边界框（minLon, minLat, maxLon, maxLat） | `97.095, 37.295, 126.105, 53.405` |
| `Creation Time` | 转换的 UTC 时间戳 | `2026-05-26 12:08:29` |
| `Source` | 数据来源名称 | `hfioi` |
| `Compression` | 压缩算法 | `DEFLATE` |
| `startX` / `startY` | 左上角坐标 | `97.095000` / `53.405000` |
| `endX` / `endY` | 右下角坐标 | `126.105000` / `37.295000` |
| `min` / `max` | 全局数据值范围 | `0.00` / `7.91` |
| `offset` / `scale` | 线性变换参数 | `0.0000` / `1.0000` |
| `unit` | 数据单位（来自 netCDF 变量属性） | `mm` |
| `NODATA` | 无效值 | `nan` |

### 数据来源配置

`Source` 字段按以下优先级确定：

1. **`--metadata-source` CLI 参数**（最高优先级）—— 显式设置来源名称
2. **netCDF 全局属性** —— 从 `source`、`platform` 或 `institution` 属性中自动检测
3. **空字符串**（默认回退值）

```bash
# 使用自定义来源名称
nc2cog --metadata-source "风云四号卫星" input.nc output/

# 从 netCDF 属性自动检测（默认行为）
nc2cog input.nc output/
```

### 查看元数据

```bash
# 查看所有元数据字段
gdalinfo output.tif

# 以 JSON 格式查看元数据
gdalinfo -json output.tif | python -c "
import json, sys
d = json.load(sys.stdin)
m = d.get('metadata', {}).get('', {})
for k, v in sorted(m.items()):
    print(f'{k}: {v}')
"
```

## 🎯 使用场景

### 气象/气候数据
```bash
nc2cog climate_data.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

### 海洋数据
```bash
nc2cog ocean_data.nc output/ \
  --compression lzw \
  --tile-size 1024 \
  --resampling bilinear \
  --overview-levels 2,4,8
```

### 大数据集处理
```bash
nc2cog large_dataset/ output/ \
  --threads 4 \
  --compression deflate \
  --zlevel 7 \
  --tile-size 512
```

### 投影转换

转换过程中支持坐标系重投影：

从 WGS84 转换为 Web Mercator：
```bash
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 input.nc output/
```

仅指定目标投影（源投影自动检测）：
```bash
nc2cog --dst-proj EPSG:3857 input.nc output/
```

结合其他转换参数：
```bash
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 \
  --compression deflate \
  --zlevel 9 \
  --tile-size 1024 \
  input.nc output/
```

## 🤝 贡献

1. Fork 本仓库
2. 创建特性分支
3. 提交你的修改
4. 如适用，添加测试
5. 提交 Pull Request

## 📄 许可证

MIT License

## 🐛 问题反馈

请在 GitHub 仓库提交 Issue。

## 📚 文档

更多详细文档请参考：
- [用户指南](docs/user_guide.md)
- [GDAL 优化详情](docs/gdal_optimization.md)
- [使用示例](docs/examples.md)
- [安装指南](INSTALLATION.md)
- [项目结构](docs/project_structure.md)

## ℹ️ 补充说明

### 概览层级生成

使用 `--overview-levels` 时，GDAL 会根据源图像尺寸智能决定实际生成的概览层级。对于较小的图像，GDAL 可能生成比指定数量更少的层级，以避免生成过小且无用的概览。

例如，在 1781x1572 的图像上使用 `--overview-levels 2,4,8,16,32`，GDAL 可能只生成层级 2 和 4（890x786 和 445x393 像素），因为更小的层级没有实用价值。

---

Made with ❤️ for the geospatial community.
