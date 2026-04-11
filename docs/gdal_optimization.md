# GDAL 优化详解

## 概述

本项目对 GDAL 相关功能进行了深度优化，旨在消除转换过程中出现的警告信息，提升处理效率和可靠性。

## GDAL 驱动参数优化

### GeoTIFF 驱动 (GTiff)

**问题**: GeoTIFF 驱动不支持 `TILEWIDTH` 和 `TILEHEIGHT` 参数

**修复前**:
```python
creation_options = [
    f'TILEWIDTH={tile_size[0]}',     # 不支持，导致警告
    f'TILEHEIGHT={tile_size[1]}',    # 不支持，导致警告
    'TILED=YES',
    # ...
]
```

**修复后**:
```python
creation_options = [
    'TILED=YES',
    f'BLOCKXSIZE={tile_size[0]}',    # 使用正确的参数
    f'BLOCKYSIZE={tile_size[1]}',    # 使用正确的参数
    # ...
]
```

### Cloud-Optimized GeoTIFF 驱动 (COG)

**问题**: COG 驱动不支持 `TILED=YES`, `COPY_SRC_OVERVIEWS`, `BLOCKXSIZE`, `BLOCKYSIZE`

**修复前**:
```python
cog_creation_options = [
    'TILED=YES',                   # 不支持，导致警告
    'COPY_SRC_OVERVIEWS=YES',      # 不支持，导致警告
    f'BLOCKXSIZE={block_size[0]}', # 不支持，导致警告
    f'BLOCKYSIZE={block_size[1]}', # 不支持，导致警告
    # ...
]
```

**修复后**:
```python
cog_creation_options = [
    f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',  # 使用支持的参数
    # ...
]
```

## 已解决的 GDAL 警告

### 旧版本警告
```
Warning 1: General options of gdal_translate make the COPY_SRC_OVERVIEWS creation option ineffective
Warning 6: driver GTiff does not support creation option LEVEL
Warning 6: driver GTiff does not support creation option TILE_WIDTH
Warning 6: driver GTiff does not support creation option TILE_HEIGHT
Warning 5: tmpfile.tif: BLOCKXSIZE can only be used with TILED=YES
Warning 6: driver COG does not support creation option TILED
Warning 6: driver COG does not support creation option COPY_SRC_OVERVIEWS
Warning 6: driver COG does not support creation option BLOCKXSIZE
Warning 6: driver COG does not support creation option BLOCKYSIZE
```

### 新版本解决方案
- 移除不兼容的参数组合
- 为不同驱动使用正确参数
- 优化概览处理流程

## 驱动程序特性对比

| 参数 | GTiff 驱动 | COG 驱动 | 说明 |
|------|------------|----------|------|
| COMPRESS | ✓ | ✓ | 压缩类型 |
| LEVEL | ✗ | ✓ | 压缩级别 |
| TILED | ✓ | ✗ | 瓦片化 |
| TILEWIDTH/TILEHEIGHT | ✗ | ✗ | 瓦片尺寸 |
| BLOCKXSIZE/BLOCKYSIZE | ✓ | ✗ | 块尺寸 |
| BLOCKSIZE | ✗ | ✓ | 块尺寸（COG版） |
| COPY_SRC_OVERVIEWS | ✓/✗* | ✗ | 拷贝源概览 |
| OVERVIEWS | ✗ | ✓ | 概览选项 |

*注：GTiff 驱动中 COPY_SRC_OVERVIEWS 与手动概览构建可能冲突

## 概览处理优化

### 旧版问题
- `COPY_SRC_OVERVIEWS=YES` 与手动 `BuildOverviews` 冲突
- 参数不匹配导致 GDAL 警告

### 新版解决方案
```python
# 在临时 GTiff 中构建概览
if overviews:
    temp_dataset = gdal.Open(str(temp_path), gdal.GA_Update)
    if temp_dataset is not None:
        resampling = overviews.get('resampling', 'nearest')
        levels = overviews.get('levels', [2, 4, 8, 16])
        temp_dataset.BuildOverviews(resampling, levels)
        temp_dataset = None

# 转换为 COG 时使用适当的概览选项
cog_creation_options = [
    f'COMPRESS={compression.upper()}',
    f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',
    f'BIGTIFF=IF_SAFER'
]

if overviews:
    cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')
```

## GDAL 异常处理

### 优化导入处理
```python
try:
    from osgeo import gdal, osr
    # 启用 GDAL 异常以获得更好的错误处理
    gdal.UseExceptions()
    GDAL_AVAILABLE = True
except ImportError as e:
    # ...
except OSError as e:
    # ...
except Exception as e:
    # ...
```

## 参数验证

### CLI 参数验证
- 使用 `click.IntRange(1, 9)` 确保 zlevel 在有效范围内
- 使用 `click.Choice` 限制可选值
- 提供清晰的帮助文本

### 配置验证
- 验证压缩类型有效性
- 验证尺寸参数正整数性
- 验证压缩级别范围

## 性能考虑

### 内存管理
- 使用临时文件而非完全加载内存
- 适当的缓存大小
- 及时释放资源

### 瓦片策略
- 根据数据特征选择瓦片大小
- 平衡读取效率与文件大小

## 配置最佳实践

### 适用于科学数据
```bash
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --tile-size 512 \
  --block-size 256 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

### 适用于快速访问
```bash
nc2cog input.nc output/ \
  --compression lzw \
  --tile-size 1024 \
  --resampling bilinear \
  --overview-levels 2,4,8
```

## 常见 GDAL 警告预防

### 预防措施
1. 了解不同驱动支持的参数
2. 避免驱动间的参数混淆
3. 使用 GDAL 1:1 传输功能时注意参数兼容性
4. 正确处理概览生成与复制

### 调试技巧
- 使用 `-v` 参数查看详细日志
- 检查 GDAL 版本兼容性
- 验证输入文件格式
- 监控内存使用情况

通过这些优化，项目现在能够更可靠地处理 netCDF 到 COG 的转换，同时提供清洁的输出，没有任何 GDAL 警告。