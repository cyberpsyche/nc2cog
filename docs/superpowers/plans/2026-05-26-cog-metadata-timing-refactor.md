# COG 元数据写入时机优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将元数据写入时机从"COG 创建后二次修改"改为"在中间 GeoTIFF 阶段写入"，从而避免破坏 COG 布局（消除 "IFD has been rewritten" 警告）。

**Architecture:** 在 `processor.py` 中，将元数据写入从 `gdal.Translate(..., format='COG')` 之后移到中间 GeoTIFF（`temp_path`）上。GDAL COG 驱动在转换时会自动携带源文件元数据到输出文件。删除不再需要的 `write_metadata_to_cog` 函数及 processor.py 中的相关调用。

**Tech Stack:** Python, GDAL (osgeo), netCDF4, pytest

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `src/nc2cog/processor.py:12` | 修改 | 删除 `write_metadata_to_cog` 导入 |
| `src/nc2cog/processor.py:150-163` | 修改 | `convert_file` 中：将元数据写入移到 `gdal.Translate(GTiff)` 之后、`gdal.Translate(COG)` 之前 |
| `src/nc2cog/processor.py:370-392` | 修改 | `_convert_variable_to_cog` 中：将元数据写入移到 temp_ds 关闭后、`gdal.Translate(COG)` 之前 |
| `src/nc2cog/metadata.py:257-272` | 修改 | 删除 `write_metadata_to_cog` 函数 |
| `src/nc2cog/metadata.py:189-193` | 修改 | `collect()` 中：min/max 扫描后需要关闭 ds（删除 FlushCache 调用，因为只读打开） |
| `tests/test_metadata.py` | 无改动 | 现有测试仍然有效，无依赖 `write_metadata_to_cog` 的测试 |

---

### Task 1: 修改 processor.py — 转换 convert_file 方法的元数据写入时机

**Files:**
- Modify: `src/nc2cog/processor.py`

- [ ] **Step 1: 修改导入，删除 write_metadata_to_cog**

将第 12 行从：
```python
from .metadata import MetadataCollector, write_metadata_to_cog
```
改为：
```python
from .metadata import MetadataCollector
```

- [ ] **Step 2: 修改 convert_file 方法中的元数据写入时机**

将第 124-165 行（从 `gdal.Translate` GTiff 完成到 `self.logger.info` 成功日志之间）的代码：

```python
                )  # end of gdal.Translate GTiff

                # Build overviews if specified
                if overviews:
                    temp_dataset = gdal.Open(str(temp_path), gdal.GA_Update)
                    if temp_dataset is not None:
                        resampling = overviews.get('resampling', 'nearest')
                        levels = overviews.get('levels', [2, 4, 8, 16])
                        temp_dataset.BuildOverviews(resampling, levels)
                        temp_dataset = None  # Properly close dataset to release file handle

                # Convert to COG format
                cog_creation_options = [
                    f'COMPRESS={compression.upper()}',
                    f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',
                    f'BIGTIFF=IF_SAFER'
                ]
                if overviews:
                    cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')

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

替换为（元数据写入移到 COG 转换之前，写入中间 GeoTIFF）：

```python
                )  # end of gdal.Translate GTiff

                # Build overviews if specified
                if overviews:
                    temp_dataset = gdal.Open(str(temp_path), gdal.GA_Update)
                    if temp_dataset is not None:
                        resampling = overviews.get('resampling', 'nearest')
                        levels = overviews.get('levels', [2, 4, 8, 16])
                        temp_dataset.BuildOverviews(resampling, levels)
                        temp_dataset = None  # Properly close dataset to release file handle

                # Write metadata to intermediate GeoTIFF before COG conversion
                # GDAL COG driver carries metadata from source to output
                try:
                    collector = MetadataCollector(self.config)
                    nc_meta = collector.collect(input_file, temp_path)
                    temp_ds = gdal.Open(str(temp_path), gdal.GA_Update)
                    if temp_ds is not None:
                        temp_ds.SetMetadata(nc_meta)
                        temp_ds = None
                except Exception as meta_err:
                    self.logger.warning(f"Failed to write metadata: {meta_err}")

                # Convert to COG format
                cog_creation_options = [
                    f'COMPRESS={compression.upper()}',
                    f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',
                    f'BIGTIFF=IF_SAFER'
                ]
                if overviews:
                    cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')

                gdal.Translate(
                    str(output_file),
                    str(temp_path),
                    format='COG',
                    creationOptions=cog_creation_options
                )

                self.logger.info(f"Successfully converted: {input_file}")
```

- [ ] **Step 3: Commit**

```bash
git add src/nc2cog/processor.py
git commit -m "refactor: write metadata to intermediate GeoTIFF instead of modifying COG after creation"
```

---

### Task 2: 修改 processor.py — 转换 _convert_variable_to_cog 方法的元数据写入时机

**Files:**
- Modify: `src/nc2cog/processor.py`

- [ ] **Step 1: 修改 _convert_variable_to_cog 方法中的元数据写入时机**

将第 360-394 行（从 `temp_ds = None` 到 `self.logger.info` 成功日志之间）的代码：

```python
            temp_ds = None

            # Build overviews
            if overviews:
                temp_ds = gdal.Open(str(temp_path), gdal.GA_Update)
                if temp_ds is not None:
                    resampling = overviews.get('resampling', 'nearest')
                    levels = overviews.get('levels', [2, 4, 8, 16])
                    temp_ds.BuildOverviews(resampling, levels)
                    temp_ds = None

            # Convert to COG
            cog_creation_options = [
                f'COMPRESS={compression.upper()}',
                f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',
                'BIGTIFF=IF_SAFER',
            ]
            if overviews:
                cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')

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

替换为（元数据写入移到 COG 转换之前，写入中间 GeoTIFF）：

```python
            temp_ds = None

            # Build overviews
            if overviews:
                temp_ds = gdal.Open(str(temp_path), gdal.GA_Update)
                if temp_ds is not None:
                    resampling = overviews.get('resampling', 'nearest')
                    levels = overviews.get('levels', [2, 4, 8, 16])
                    temp_ds.BuildOverviews(resampling, levels)
                    temp_ds = None

            # Write metadata to intermediate GeoTIFF before COG conversion
            # GDAL COG driver carries metadata from source to output
            try:
                collector = MetadataCollector(self.config)
                nc_meta = collector.collect(input_file, temp_path, var_name)
                temp_ds = gdal.Open(str(temp_path), gdal.GA_Update)
                if temp_ds is not None:
                    temp_ds.SetMetadata(nc_meta)
                    temp_ds = None
            except Exception as meta_err:
                self.logger.warning(f"Failed to write metadata: {meta_err}")

            # Convert to COG
            cog_creation_options = [
                f'COMPRESS={compression.upper()}',
                f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',
                'BIGTIFF=IF_SAFER',
            ]
            if overviews:
                cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')

            gdal.Translate(
                str(output_file),
                str(temp_path),
                format='COG',
                creationOptions=cog_creation_options
            )

            self.logger.info(f"Successfully converted {var_name} -> {output_file.name}")
```

- [ ] **Step 2: Commit**

```bash
git add src/nc2cog/processor.py
git commit -m "refactor: write metadata to intermediate GeoTIFF in _convert_variable_to_cog"
```

---

### Task 3: 从 metadata.py 中删除 write_metadata_to_cog 函数

**Files:**
- Modify: `src/nc2cog/metadata.py`

- [ ] **Step 1: 删除 write_metadata_to_cog 函数**

删除第 257-272 行的整个函数：

```python
def write_metadata_to_cog(cog_path: Path, metadata: Dict[str, str]):
    """Open a COG file and write all metadata via GDAL SetMetadata."""
    if not GDAL_AVAILABLE:
        raise ConversionError("GDAL is required to write metadata")

    ds = gdal.OpenEx(
        str(cog_path),
        gdal.OF_UPDATE,
        open_options=['IGNORE_COG_LAYOUT_BREAK=YES'],
    )
    if ds is None:
        raise ConversionError(f"Cannot open COG file for metadata update: {cog_path}")

    ds.SetMetadata(metadata)
    ds.FlushCache()
    ds = None  # Close and flush
```

- [ ] **Step 2: 删除 collect() 末尾不必要的 FlushCache**

`collect()` 方法以只读方式打开 GeoTIFF（`gdal.Open`），不需要 `FlushCache()`。将第 195 行的 `ds.FlushCache()` 删除，保留 `ds = None`。

- [ ] **Step 3: Commit**

```bash
git add src/nc2cog/metadata.py
git commit -m "chore: remove write_metadata_to_cog function, no longer needed"
```

---

### Task 4: 验证 — 运行全部测试确保无回归

**Files:**
- No file changes

- [ ] **Step 1: 运行全部测试**

Run: `python -m pytest tests/ -v`
Expected: All 58 tests pass

- [ ] **Step 2: Commit（如果测试通过）**

```bash
git add tests/
git commit -m "test: verify all tests pass after metadata timing refactor"
```

---

### Task 5: 端到端验证 — 确认 COG 布局不再被破坏

**Files:**
- No file changes

- [ ] **Step 1: 执行一次完整转换**

Run: `rm -f /tmp/test_cog.tif && nc2cog tests/data/sample.nc /tmp/test_cog.tif -v 2>&1`
Expected: No "IFD has been rewritten" or "COG layout" warnings in output

- [ ] **Step 2: 用 gdalinfo 验证无警告**

Run: `gdalinfo /tmp/test_cog.tif 2>&1 | grep -i "layout\|rewritten\|invalidated"`
Expected: No output (no warnings)

- [ ] **Step 3: 验证元数据完整**

Run: `gdalinfo -json /tmp/test_cog.tif | python -c "import json,sys; d=json.load(sys.stdin); m=d.get('metadata',{}).get('',''); [print(f'{k}: {v}') for k,v in sorted(m.items())]"`
Expected: All 18 fields present

- [ ] **Step 4: 清理**

```bash
rm -f /tmp/test_cog.tif
```
