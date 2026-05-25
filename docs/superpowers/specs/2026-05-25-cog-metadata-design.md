# COG TIFF 元数据写入设计

**日期:** 2026-05-25
**状态:** 待审批

## 目标

在 nc2cog 转换生成的 COG TIFF 文件中，通过 GDAL 元数据域写入 18 个标准化元数据标签，确保数据可识别、可追溯。

## 新增模块：`src/nc2cog/metadata.py`

### `MetadataCollector` 类

职责：从 netCDF 源文件、中间 GeoTIFF、配置中收集全部元数据，组装为键值字典。

#### 核心方法

```python
class MetadataCollector:
    def __init__(self, config_manager):
        # 读取配置中的 metadata.source 兜底值
        self.fallback_source = config_manager.get('metadata.source', None)

    def collect(self, nc_file: Path, temp_tiff_path: Path, variable_name: Optional[str] = None) -> Dict[str, str]:
        """收集全部元数据，返回键值字典。"""
```

#### 字段收集策略

| 字段 | 数据来源 | 说明 |
|------|---------|------|
| Coordinate System | 目标投影配置 / GeoTIFF 投影 WKT | 若启用了投影转换，使用 target_projection 的 WKT；否则使用源文件投影 WKT。同时在值中标注 "WGS84 (EPSG:4326)" 字样 |
| Band Count | GDAL 临时 GeoTIFF `RasterCount` | 直接从打开的 temp_tiff_path 读取 |
| Data Type | GDAL 临时 GeoTIFF `GetRasterBand(1).DataType` | 映射为 GDAL 数据类型名称（Float32、UInt16、UInt8 等） |
| Resolution | GeoTransform[1]（X方向分辨率） | 保留 8 位小数，单位为度 |
| Extent | GeoTransform + 宽高计算 | minLon, minLat, maxLon, maxLat，保留 6-8 位小数 |
| Creation Time | 当前 UTC 时间 | `datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')` |
| Source | netCDF global attributes → 配置兜底 | 依次尝试读取 netCDF 的 `source`、`platform`、`institution` 属性；都为空时使用 `config_manager.get('metadata.source')` |
| Compression | 配置 `compression` 字段 | 转为大写（DEFLATE、LZW、JPEG） |
| startX | GeoTransform[0] | 左上角经度，保留 6-8 位小数 |
| startY | GeoTransform[3] | 左上角纬度，保留 6-8 位小数 |
| endX | GeoTransform[0] + width × GeoTransform[1] | 右下角经度，保留 6-8 位小数 |
| endY | GeoTransform[3] + height × GeoTransform[5] | 右下角纬度，保留 6-8 位小数 |
| max | 扫描 temp_tiff_path 所有波段的最大值 | 全局统计，保留 2-4 位小数 |
| min | 扫描 temp_tiff_path 所有波段的最小值 | 全局统计，保留 2-4 位小数 |
| offset | 配置 `metadata.offset`，默认 0.0 | 保留 4 位小数 |
| scale | 配置 `metadata.scale`，默认 1.0 | 保留 4 位小数 |
| unit | 配置 `metadata.unit`，或从 netCDF 变量 attributes 提取 | 优先读取变量的 `units` attribute，兜底用配置值 |
| NODATA | 固定值 `-9999.0` | 按需可配置 |

#### 返回值格式

键名使用上表中的字段名（如 `"Coordinate System"`, `"Band Count"` 等），值为字符串。

### `metadata_writer` 函数

```python
def write_metadata_to_cog(cog_path: Path, metadata: Dict[str, str]):
    """打开 COG 文件，通过 gdal.SetMetadata() 一次性写入全部元数据。"""
```

使用 `gdal.Open(str(cog_path), gdal.GA_Update)` 打开文件，调用 `dataset.SetMetadata(metadata, domain='')` 写入默认域。

## 命令行变更

仅新增 **1 个** CLI 参数：

| 参数 | 说明 | 默认行为 |
|------|------|---------|
| `--metadata-source` | 数据源描述（如卫星、传感器名称） | 不指定时自动从 netCDF global attributes（`source`、`platform`、`institution`）提取，提取不到时使用配置文件 `metadata.source` 兜底 |

其余元数据字段（`offset`、`scale`、`unit`）通过配置文件管理，不上 CLI：

```bash
# 示例：指定数据源的转换命令
nc2cog input.nc output.tif --metadata-source "Sentinel-2"

# 不指定时，自动提取兜底
nc2cog input.nc output.tif
```

## 配置变更

在 `default_config.yaml` 中新增 `metadata` 配置块：

```yaml
metadata:
  source: ""        # 数据源兜底值
  offset: 0.0       # 默认偏移量
  scale: 1.0        # 默认缩放比例
  unit: ""          # 数据单位兜底值
```

### `cli.py` 参数处理

新增 `--metadata-source` 参数，在 CLI 函数签名中追加：

```python
@click.option('--metadata-source', type=str, default=None,
              help='Data source description for metadata (e.g., satellite, sensor)')
```

若用户传入了该参数，则覆盖配置中的 `metadata.source`：

```python
if metadata_source:
    config_manager.config['metadata'] = config_manager.config.get('metadata', {})
    config_manager.config['metadata']['source'] = metadata_source
```

## 集成点

### `convert_file`（单变量转换）

在 `gdal.Translate(..., format='COG', ...)` 成功后：
1. 调用 `MetadataCollector.collect(input_file, temp_path)` 收集元数据
2. 调用 `write_metadata_to_cog(output_file, metadata)` 写入

### `convert_multiband_file`（多变量/多波段转换）

在 `gdal.Translate(..., format='COG', ...)` 成功后：
1. 调用 `MetadataCollector.collect(input_file, temp_path, variable_name)` 收集元数据
2. 调用 `write_metadata_to_cog(output_file, metadata)` 写入

由于 max/min 为全局一组（方案 A），多波段文件也只记录一组全局统计。

## 依赖

- 现有依赖不变（GDAL、netCDF4、numpy）
- 新增标准库 `datetime` 用于 Creation Time

## 测试

- `tests/test_metadata.py`: 单元测试 `MetadataCollector.collect()` 返回的键值对
- 集成测试：转换一个测试 netCDF 文件，用 `gdalinfo -json output.tif` 验证元数据域中各字段存在且值正确
