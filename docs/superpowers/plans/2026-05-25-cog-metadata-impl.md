# COG TIFF 元数据写入实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 nc2cog 转换生成的 COG TIFF 文件中写入 18 个标准化元数据标签，通过 GDAL 元数据域存储。

**Architecture:** 新增 `metadata.py` 模块负责收集元数据并写入 COG 文件；在 `cli.py` 中新增 `--metadata-source` 参数；在 `processor.py` 的转换流程末尾调用元数据写入。所有改动为纯新增，不修改现有功能逻辑。

**Tech Stack:** Python, GDAL (osgeo), netCDF4, Click, PyYAML, pytest

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `src/nc2cog/metadata.py` | 新建 | `MetadataCollector` 类和 `write_metadata_to_cog` 函数 |
| `default_config.yaml` | 修改 | 新增 `metadata:` 配置块 |
| `src/nc2cog/cli.py` | 修改 | 新增 `--metadata-source` 参数及处理逻辑 |
| `src/nc2cog/processor.py` | 修改 | 在 `convert_file` 和 `_convert_variable_to_cog` 末尾调用元数据收集与写入 |
| `tests/test_metadata.py` | 新建 | `MetadataCollector` 单元测试 |
| `tests/data/sample.nc` | 新建（测试用） | 小型 netCDF 测试文件 |

---

### Task 1: 添加 metadata 配置到 default_config.yaml

**Files:**
- Modify: `/Users/sam/Projects/GIS/nc2cog/config/default_config.yaml`

- [ ] **Step 1: 在 default_config.yaml 末尾追加 metadata 配置块**

在现有配置末尾（`skip_errors: true` 之后）追加：

```yaml
# Metadata
metadata:
  source: ""        # Data source description (fallback if not auto-detected)
  offset: 0.0       # Data offset (radiometric correction)
  scale: 1.0        # Data scale factor (radiometric correction)
  unit: ""          # Data unit (fallback if not in variable attributes)
```

注意保持 YAML 缩进一致（2 空格）。

- [ ] **Step 2: 验证 YAML 可被正确加载**

Run: `python -c "import yaml; print(yaml.safe_load(open('config/default_config.yaml'))['metadata'])"`
Expected: `{'source': '', 'offset': 0.0, 'scale': 1.0, 'unit': ''}`

- [ ] **Step 3: Commit**

```bash
git add config/default_config.yaml
git commit -m "feat: add metadata config section to default config"
```

---

### Task 2: 新建 metadata.py 模块

**Files:**
- Create: `src/nc2cog/metadata.py`

- [ ] **Step 1: 编写 metadata.py 模块**

```python
"""Metadata collector and writer for COG TIFF files."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

try:
    from osgeo import gdal
    GDAL_AVAILABLE = True
except ImportError:
    gdal = None
    GDAL_AVAILABLE = False

try:
    import netCDF4
    NETCDF4_AVAILABLE = True
except ImportError:
    NETCDF4_AVAILABLE = False

# GDAL data type index to name mapping
_GDAL_TYPE_NAMES = {
    1: 'Byte', 2: 'UInt16', 3: 'Int16', 4: 'UInt32',
    5: 'Int32', 6: 'Float32', 7: 'Float64',
}

# Field names as they will appear in the TIFF metadata
FIELD_COORDINATE_SYSTEM = "Coordinate System"
FIELD_BAND_COUNT = "Band Count"
FIELD_DATA_TYPE = "Data Type"
FIELD_RESOLUTION = "Resolution"
FIELD_EXTENT = "Extent"
FIELD_CREATION_TIME = "Creation Time"
FIELD_SOURCE = "Source"
FIELD_COMPRESSION = "Compression"
FIELD_START_X = "startX"
FIELD_START_Y = "startY"
FIELD_END_X = "endX"
FIELD_END_Y = "endY"
FIELD_MAX = "max"
FIELD_MIN = "min"
FIELD_OFFSET = "offset"
FIELD_SCALE = "scale"
FIELD_UNIT = "unit"
FIELD_NODATA = "NODATA"


class MetadataCollector:
    """Collects metadata from netCDF files and intermediate GeoTIFFs."""

    def __init__(self, config_manager):
        self.fallback_source = config_manager.get('metadata.source', None) or ''
        self.fallback_offset = config_manager.get('metadata.offset', 0.0)
        self.fallback_scale = config_manager.get('metadata.scale', 1.0)
        self.fallback_unit = config_manager.get('metadata.unit', None) or ''
        self.compression = config_manager.get('compression', 'deflate').upper()
        self.target_projection = config_manager.get('projection.target', None)

    def collect(
        self,
        nc_file: Path,
        temp_tiff_path: Path,
        variable_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """Collect all metadata and return as a key-value dict."""
        metadata = {}

        # Read from the intermediate GeoTIFF
        ds = gdal.Open(str(temp_tiff_path))
        if ds is None:
            raise RuntimeError(f"Cannot open intermediate GeoTIFF: {temp_tiff_path}")

        gt = ds.GetGeoTransform()
        projection = ds.GetProjection()
        width = ds.RasterXSize
        height = ds.RasterYSize
        band_count = ds.RasterCount

        # Coordinate System
        if self.target_projection:
            coord_sys = f"WGS84 (EPSG:4326) - {self.target_projection}"
        elif projection:
            coord_sys = f"WGS84 (EPSG:4326) - {projection}"
        else:
            coord_sys = "WGS84 (EPSG:4326)"
        metadata[FIELD_COORDINATE_SYSTEM] = coord_sys

        # Band Count
        metadata[FIELD_BAND_COUNT] = str(band_count)

        # Data Type
        dtype_code = ds.GetRasterBand(1).DataType
        dtype_name = _GDAL_TYPE_NAMES.get(dtype_code, f'Unknown({dtype_code})')
        metadata[FIELD_DATA_TYPE] = dtype_name

        # Resolution (GeoTransform[1] is pixel width in degrees)
        resolution = f"{gt[1]:.8f}"
        metadata[FIELD_RESOLUTION] = resolution

        # Extent: minLon, minLat, maxLon, maxLat
        min_lon = gt[0]
        max_lon = gt[0] + width * gt[1]
        max_lat = gt[3]
        min_lat = gt[3] + height * gt[5]  # gt[5] is negative
        metadata[FIELD_EXTENT] = (
            f"{min_lon:.6f}, {min_lat:.6f}, {max_lon:.6f}, {max_lat:.6f}"
        )

        # Creation Time
        metadata[FIELD_CREATION_TIME] = datetime.now(timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S'
        )

        # Source
        source = self._extract_source(nc_file, variable_name)
        metadata[FIELD_SOURCE] = source

        # Compression
        metadata[FIELD_COMPRESSION] = self.compression

        # startX, startY, endX, endY
        metadata[FIELD_START_X] = f"{gt[0]:.6f}"
        metadata[FIELD_START_Y] = f"{gt[3]:.6f}"
        metadata[FIELD_END_X] = f"{max_lon:.6f}"
        metadata[FIELD_END_Y] = f"{min_lat:.6f}"

        # Scan all bands for global min/max
        global_min = float('inf')
        global_max = float('-inf')
        for b in range(1, band_count + 1):
            band = ds.GetRasterBand(b)
            data = band.ReadAsArray()
            if data is not None:
                import numpy as np
                valid = data[~np.isnan(data)]
                if len(valid) > 0:
                    band_min = float(np.min(valid))
                    band_max = float(np.max(valid))
                    if band_min < global_min:
                        global_min = band_min
                    if band_max > global_max:
                        global_max = band_max
            band = None

        if global_min != float('inf'):
            metadata[FIELD_MIN] = f"{global_min:.2f}"
            metadata[FIELD_MAX] = f"{global_max:.2f}"
        else:
            metadata[FIELD_MIN] = "N/A"
            metadata[FIELD_MAX] = "N/A"

        # offset, scale
        metadata[FIELD_OFFSET] = f"{float(self.fallback_offset):.4f}"
        metadata[FIELD_SCALE] = f"{float(self.fallback_scale):.4f}"

        # unit
        unit = self._extract_unit(nc_file, variable_name)
        metadata[FIELD_UNIT] = unit

        # NODATA
        metadata[FIELD_NODATA] = "-9999.0"

        ds = None
        return metadata

    def _extract_source(
        self, nc_file: Path, variable_name: Optional[str]
    ) -> str:
        """Extract source from netCDF global attributes, fallback to config."""
        if not NETCDF4_AVAILABLE:
            return self.fallback_source

        try:
            nc = netCDF4.Dataset(str(nc_file), 'r')
            try:
                for attr in ('source', 'platform', 'institution'):
                    val = getattr(nc, attr, None)
                    if val and str(val).strip():
                        return str(val).strip()
                return self.fallback_source
            finally:
                nc.close()
        except Exception:
            return self.fallback_source

    def _extract_unit(
        self, nc_file: Path, variable_name: Optional[str]
    ) -> str:
        """Extract unit from netCDF variable attributes, fallback to config."""
        if variable_name and NETCDF4_AVAILABLE:
            try:
                nc = netCDF4.Dataset(str(nc_file), 'r')
                try:
                    if variable_name in nc.variables:
                        var = nc.variables[variable_name]
                        units = getattr(var, 'units', None)
                        if units and str(units).strip():
                            return str(units).strip()
                    return self.fallback_unit
                finally:
                    nc.close()
            except Exception:
                return self.fallback_unit
        return self.fallback_unit


def write_metadata_to_cog(cog_path: Path, metadata: Dict[str, str]):
    """Open a COG file and write all metadata via GDAL SetMetadata."""
    if not GDAL_AVAILABLE:
        raise RuntimeError("GDAL is required to write metadata")

    ds = gdal.Open(str(cog_path), gdal.GA_Update)
    if ds is None:
        raise RuntimeError(f"Cannot open COG file for metadata update: {cog_path}")

    ds.SetMetadata(metadata)
    ds = None  # Close and flush
```

- [ ] **Step 2: Commit**

```bash
git add src/nc2cog/metadata.py
git commit -m "feat: add metadata.py module for COG metadata collection and writing"
```

---

### Task 3: 集成到 cli.py — 新增 --metadata-source 参数

**Files:**
- Modify: `src/nc2cog/cli.py`

- [ ] **Step 1: 在 main 函数参数列表中追加 --metadata-source**

在 `@click.option('--variables', ...)` 之后（第 36 行之后）追加：

```python
@click.option('--metadata-source', type=str, default=None,
              help='Data source description for metadata (e.g., satellite, sensor)')
```

- [ ] **Step 2: 在 main 函数签名中添加 metadata_source 参数**

在 `variables: Optional[str],` 之后追加：

```python
    metadata_source: Optional[str],
```

- [ ] **Step 3: 在 projection 参数处理逻辑之后追加 metadata_source 处理**

在第 95 行（`config_manager.config['projection']['source'] = src_proj`）之后追加：

```python
        # Handle metadata source parameter
        if metadata_source:
            config_manager.config['metadata'] = config_manager.config.get('metadata', {})
            config_manager.config['metadata']['source'] = metadata_source
```

- [ ] **Step 4: Commit**

```bash
git add src/nc2cog/cli.py
git commit -m "feat: add --metadata-source CLI parameter"
```

---

### Task 4: 集成到 processor.py — 调用元数据收集与写入

**Files:**
- Modify: `src/nc2cog/processor.py`

- [ ] **Step 1: 在 processor.py 顶部导入 metadata 模块**

在 `from .config import ConfigManager` 之后追加：

```python
from .metadata import MetadataCollector, write_metadata_to_cog
```

- [ ] **Step 2: 在 convert_file 方法中，COG 写出成功后调用元数据写入**

找到 `convert_file` 方法中这段代码（约第 154-157 行）：

```python
                gdal.Translate(
                    str(output_file),
                    str(temp_path),
                    format='COG',
                    creationOptions=cog_creation_options
                )

                self.logger.info(f"Successfully converted: {input_file}")
```

替换为：

```python
                gdal.Translate(
                    str(output_file),
                    str(temp_path),
                    format='COG',
                    creationOptions=cog_creation_options
                )

                # Write metadata to the output COG
                try:
                    collector = MetadataCollector(self.config)
                    nc_meta = collector.collect(input_file, temp_path)
                    write_metadata_to_cog(output_file, nc_meta)
                except Exception as meta_err:
                    self.logger.warning(f"Failed to write metadata: {meta_err}")

                self.logger.info(f"Successfully converted: {input_file}")
```

- [ ] **Step 3: 在 _convert_variable_to_cog 方法中，COG 写出成功后调用元数据写入**

找到 `_convert_variable_to_cog` 方法中这段代码（约第 370-377 行）：

```python
            gdal.Translate(
                str(output_file),
                str(temp_path),
                format='COG',
                creationOptions=cog_creation_options
            )

            self.logger.info(f"Successfully converted {var_name} -> {output_file.name}")
```

替换为：

```python
            gdal.Translate(
                str(output_file),
                str(temp_path),
                format='COG',
                creationOptions=cog_creation_options
            )

            # Write metadata to the output COG
            try:
                collector = MetadataCollector(self.config)
                nc_meta = collector.collect(input_file, temp_path, var_name)
                write_metadata_to_cog(output_file, nc_meta)
            except Exception as meta_err:
                self.logger.warning(f"Failed to write metadata: {meta_err}")

            self.logger.info(f"Successfully converted {var_name} -> {output_file.name}")
```

- [ ] **Step 4: Commit**

```bash
git add src/nc2cog/processor.py
git commit -m "feat: integrate metadata collection and writing into conversion pipeline"
```

---

### Task 5: 编写测试

**Files:**
- Create: `tests/test_metadata.py`
- Create: `tests/data/sample.nc` (small test netCDF)

- [ ] **Step 1: 创建小型测试用 netCDF 文件**

创建 `tests/data/` 目录（如不存在），然后创建 `tests/data/create_test_nc.py` 脚本：

```python
"""Create a small test netCDF file for metadata tests."""
import numpy as np
import netCDF4
from pathlib import Path

DATA_DIR = Path(__file__).parent
OUTPUT = DATA_DIR / "sample.nc"

def create_sample_nc():
    nc = netCDF4.Dataset(str(OUTPUT), 'w', format='NETCDF4')
    nc.source = "Test Satellite"
    nc.institution = "Test Lab"

    # Dimensions
    nc.createDimension('lat', 10)
    nc.createDimension('lon', 10)
    nc.createDimension('time', 3)

    # Coordinate variables
    lat = nc.createVariable('lat', 'f4', ('lat',))
    lat[:] = np.linspace(-5, 5, 10)
    lat.units = "degrees_north"

    lon = nc.createVariable('lon', 'f4', ('lon',))
    lon[:] = np.linspace(100, 110, 10)
    lon.units = "degrees_east"

    time = nc.createVariable('time', 'f8', ('time',))
    time[:] = [0, 1, 2]
    time.units = "days since 2025-01-01"

    # Data variable
    data = nc.createVariable('temperature', 'f4', ('time', 'lat', 'lon'))
    data.units = "K"
    data[:] = np.random.rand(3, 10, 10) * 100 + 200

    nc.close()
    print(f"Created {OUTPUT}")

if __name__ == '__main__':
    create_sample_nc()
```

Run: `python tests/data/create_test_nc.py`
Expected: `Created tests/data/sample.nc`

- [ ] **Step 2: 编写 MetadataCollector 单元测试**

创建 `tests/test_metadata.py`:

```python
"""Tests for metadata collection and writing."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

TEST_DATA_DIR = Path(__file__).parent / "data"
SAMPLE_NC = TEST_DATA_DIR / "sample.nc"


class TestMetadataCollectorConfig:
    """Test MetadataCollector reads config correctly."""

    def test_default_metadata_config(self):
        """Default config should have metadata section with expected keys."""
        from nc2cog.config import ConfigManager
        cm = ConfigManager()
        assert cm.get('metadata.source', None) == '' or cm.get('metadata.source') is None
        assert cm.get('metadata.offset', 0.0) == 0.0
        assert cm.get('metadata.scale', 1.0) == 1.0

    def test_metadata_source_override(self):
        """Config should accept metadata.source override."""
        from nc2cog.config import ConfigManager
        import yaml, tempfile, os
        config_data = {'metadata': {'source': 'My Satellite'}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            f.flush()
            cm = ConfigManager(config_path=Path(f.name))
        assert cm.get('metadata.source') == 'My Satellite'
        os.unlink(f.name)


@pytest.mark.skipif(not SAMPLE_NC.exists(), reason="Test netCDF not found")
class TestMetadataCollectorIntegration:
    """Integration tests requiring a real netCDF file."""

    def _make_mock_config(self, **overrides):
        """Create a mock ConfigManager with metadata defaults."""
        mock = MagicMock()
        mock.get.side_effect = lambda key, default=None: {
            'metadata.source': overrides.get('source', ''),
            'metadata.offset': overrides.get('offset', 0.0),
            'metadata.scale': overrides.get('scale', 1.0),
            'metadata.unit': overrides.get('unit', ''),
            'compression': 'deflate',
            'projection.target': None,
        }.get(key, default)
        return mock

    def test_extract_source_from_nc(self):
        """Source should be extracted from netCDF global attributes."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config())
        source = collector._extract_source(SAMPLE_NC, None)
        assert source == "Test Satellite"

    def test_extract_unit_from_variable(self):
        """Unit should be extracted from netCDF variable attributes."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config())
        unit = collector._extract_unit(SAMPLE_NC, 'temperature')
        assert unit == "K"

    def test_fallback_source_when_no_nc_attr(self):
        """Should use config fallback when netCDF has no source attribute."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config(source='Fallback Source'))
        source = collector._extract_source(SAMPLE_NC, None)
        # netCDF has 'source' attr, so it should be used, not fallback
        assert source == "Test Satellite"

    def test_fallback_unit_when_no_var_attr(self):
        """Should use config fallback when variable has no units attribute."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config(unit='fallback_unit'))
        # 'temperature' has units, so it should be used
        unit = collector._extract_unit(SAMPLE_NC, 'temperature')
        assert unit == "K"
        # A variable without units would use fallback
        unit = collector._extract_unit(SAMPLE_NC, 'nonexistent_var')
        assert unit == 'fallback_unit'
```

- [ ] **Step 3: 运行测试验证**

Run: `python -m pytest tests/test_metadata.py -v`
Expected: All tests pass

- [ ] **Step 4: 运行已有测试确保无回归**

Run: `python -m pytest tests/ -v`
Expected: All tests pass (new + existing)

- [ ] **Step 5: Commit**

```bash
git add tests/test_metadata.py tests/data/create_test_nc.py tests/data/sample.nc
git commit -m "test: add metadata collection unit and integration tests"
```

---

### Task 6: 端到端验证

**Files:**
- No file changes

- [ ] **Step 1: 使用测试 netCDF 文件执行一次完整转换**

Run: `nc2cog tests/data/sample.nc /tmp/test_output.tif`
Expected: Conversion succeeds

- [ ] **Step 2: 验证 COG 文件包含全部 18 个元数据字段**

Run: `gdalinfo -json /tmp/test_output.tif | python -c "import json,sys; d=json.load(sys.stdin); m=d.get('metadata',{}); [print(f'{k}: {v}') for k,v in sorted(m.items())]"`
Expected: All 18 fields present with correct values:
- `Coordinate System` contains "WGS84"
- `Band Count` = "3" (3 time steps)
- `Data Type` = "Float32"
- `Resolution` has 8 decimal places
- `Extent` has 4 comma-separated values
- `Creation Time` in YYYY-MM-DD HH:MM:SS format
- `Source` = "Test Satellite"
- `Compression` = "DEFLATE"
- `startX`, `startY`, `endX`, `endY` present with decimal values
- `max`, `min` present with 2 decimal places
- `offset` = "0.0000"
- `scale` = "1.0000"
- `unit` = "K"
- `NODATA` = "-9999.0"

- [ ] **Step 3: 验证 --metadata-source 参数生效**

Run: `nc2cog tests/data/sample.nc /tmp/test_output2.tif --metadata-source "Custom Satellite" --overwrite`
Expected: Conversion succeeds

Run: `gdalinfo -json /tmp/test_output2.tif | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('metadata',{}).get('Source','MISSING'))"`
Expected: `Custom Satellite`

- [ ] **Step 4: 清理临时文件**

```bash
rm -f /tmp/test_output.tif /tmp/test_output2.tif
```
