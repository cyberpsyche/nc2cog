# Fix 4D netCDF Support — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix conversion of netCDF files with extra singleton dimensions (e.g. `(time, z=1, y, x)`) by improving coordinate-variable detection and squeezing non-spatial dimensions before band writes.

**Architecture:** Three focused changes across three existing modules: (1) rename and share `COORD_NAMES` constant, (2) add CF-convention coordinate-variable detection in `get_data_variables()`, (3) apply `np.squeeze()` with a dimension guard in `_convert_variable_to_cog()`.

**Tech Stack:** Python 3.9+, netCDF4, NumPy, GDAL

## Global Constraints

- Python >= 3.9
- Zero behaviour change for standard `(time, y, x)` files
- Follow existing code style (type hints, docstrings, comment density)
- No new dependencies
- All existing tests must continue to pass

---

### Task 1: Share `COORD_NAMES` constant between analyzer and metadata

**Files:**
- Modify: `src/nc2cog/analyzer.py:7-10`
- Modify: `src/nc2cog/metadata.py:10-13, 242`

**Interfaces:**
- Produces: `COORD_NAMES` — public frozenset exported from `analyzer.py`, imported by `metadata.py`

- [ ] **Step 1: Rename `_COORD_NAMES` to `COORD_NAMES` in analyzer.py**

```python
# Line 7-10, change from:
_COORD_NAMES = frozenset({
    'lat', 'lon', 'latitude', 'longitude', 'time', 'crs',
    'x', 'y', 'spatial_ref', 'nav_lat', 'nav_lon',
})

# To:
COORD_NAMES = frozenset({
    'lat', 'lon', 'latitude', 'longitude', 'time', 'crs',
    'x', 'y', 'spatial_ref', 'nav_lat', 'nav_lon',
})
```

- [ ] **Step 2: Update the one reference in analyzer.py**

In `get_data_variables()` (line 71), change `_COORD_NAMES` to `COORD_NAMES`:

```python
# Line 71, change from:
if name.lower() in _COORD_NAMES:

# To:
if name.lower() in COORD_NAMES:
```

- [ ] **Step 3: In metadata.py, delete local `_COORD_NAMES` and import from analyzer**

Delete lines 10-13:

```python
# Delete these four lines:
_COORD_NAMES = frozenset({
    'lat', 'lon', 'latitude', 'longitude', 'time', 'crs',
    'x', 'y', 'spatial_ref', 'nav_lat', 'nav_lon',
})
```

Add import near the top (after existing `.errors` import, line 28):

```python
from .analyzer import COORD_NAMES
```

- [ ] **Step 4: Update the one reference in metadata.py**

In `_extract_unit()` (line 242), change `_COORD_NAMES` to `COORD_NAMES`:

```python
# Line 242, change from:
if var_name.lower() in _COORD_NAMES:

# To:
if var_name.lower() in COORD_NAMES:
```

- [ ] **Step 5: Verify no remaining references to old name**

Run: `grep -rn "_COORD_NAMES" src/`
Expected: No matches

- [ ] **Step 6: Run existing tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add src/nc2cog/analyzer.py src/nc2cog/metadata.py
git commit -m "refactor: extract COORD_NAMES as shared package constant

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: Add CF-convention coordinate variable detection

**Files:**
- Modify: `src/nc2cog/analyzer.py:75-77`

**Interfaces:**
- Consumes: `COORD_NAMES` (from Task 1)
- Produces: `NCAnalyzer.get_data_variables()` now excludes any variable whose sole dimension has the same name as the variable itself

- [ ] **Step 1: Add the CF convention check in get_data_variables()**

In `analyzer.py`, after the existing `if var.ndim >= 1 and len(var.dimensions) >= 1:` check (currently line 75), add the CF convention filter:

```python
# Current code (lines 69-77):
for name in nc.variables:
    if name.lower() in COORD_NAMES:
        continue
    var = nc.variables[name]
    # Must be at least 1D and not a scalar metadata variable
    if var.ndim >= 1 and len(var.dimensions) >= 1:
        data_vars.append(name)

# Change to:
for name in nc.variables:
    if name.lower() in COORD_NAMES:
        continue
    var = nc.variables[name]
    # Must be at least 1D and not a scalar metadata variable
    if var.ndim >= 1 and len(var.dimensions) >= 1:
        # CF convention: a variable whose only dimension has the
        # same name as the variable is a coordinate variable
        if len(var.dimensions) == 1 and var.dimensions[0] == name:
            continue
        data_vars.append(name)
```

- [ ] **Step 2: Verify with a quick Python sanity check**

Run:
```bash
python -c "
from pathlib import Path
from src.nc2cog.analyzer import NCAnalyzer

# Test with the sample.nc (should still work)
a = NCAnalyzer(Path('tests/data/sample.nc'))
vars = a.get_data_variables()
print('Variables in sample.nc:', vars)
assert 'temperature' in vars, 'temperature should be detected'
assert 'z' not in vars, 'z should not be in sample.nc'
assert 'lat' not in vars, 'lat should be excluded'
print('PASS: sample.nc variables correct')
"
```
Expected: PASS

- [ ] **Step 3: Run existing tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add src/nc2cog/analyzer.py
git commit -m "feat: add CF-convention coordinate variable detection

Auto-detect and exclude coordinate variables like z(z), height(height)
whose only dimension shares the variable name, per CF-1.8 conventions.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: Squeeze non-spatial singleton dimensions before band write

**Files:**
- Modify: `src/nc2cog/processor.py:340-348`

**Interfaces:**
- Consumes: `numpy` (already imported as `np`)
- Produces: `_convert_variable_to_cog()` now correctly handles data arrays with extra size-1 dimensions

- [ ] **Step 1: Add np.squeeze() and dimension guard in _convert_variable_to_cog()**

In `processor.py`, after the if/else block that reads data (currently lines 340-348), and before the fill value handling (line 350), add:

```python
# Current code (lines 339-355):
# Read data and write each timestep as a band
for t in range(time_steps):
    if time_steps == 1:
        # No time dimension - read entire array
        data = var[:]
    else:
        # Build slice for this timestep
        slices = [slice(None)] * len(dims)
        slices[dims.index(time_dim_name)] = t
        data = var[tuple(slices)]

    # Fill value handling
    fill_value = getattr(var, '_FillValue', None)
    if fill_value is not None:
        data = np.where(data == fill_value, -9999.0, data)

    band = temp_ds.GetRasterBand(t + 1)
    band.WriteArray(data.astype(np.float32))

# Change to:
# Read data and write each timestep as a band
for t in range(time_steps):
    if time_steps == 1:
        # No time dimension - read entire array
        data = var[:]
    else:
        # Build slice for this timestep
        slices = [slice(None)] * len(dims)
        slices[dims.index(time_dim_name)] = t
        data = var[tuple(slices)]

    # Remove singleton dimensions (e.g. z=1) so data is 2D
    data = np.squeeze(data)
    if data.ndim != 2:
        raise ConversionError(
            f"Expected 2D data after squeezing, got {data.ndim}D "
            f"with shape {data.shape} for variable {var_name}"
        )

    # Fill value handling
    fill_value = getattr(var, '_FillValue', None)
    if fill_value is not None:
        data = np.where(data == fill_value, -9999.0, data)

    band = temp_ds.GetRasterBand(t + 1)
    band.WriteArray(data.astype(np.float32))
```

- [ ] **Step 2: Verify squeeze behaviour with a quick Python check**

Run:
```bash
python -c "
import numpy as np

# Simulate various shapes
assert np.squeeze(np.zeros((100, 100))).ndim == 2, '2D stays 2D'
assert np.squeeze(np.zeros((1, 100, 100))).ndim == 2, '3D (time=1) -> 2D'
assert np.squeeze(np.zeros((1, 1, 100, 100))).ndim == 2, '4D (time=1, z=1) -> 2D'
assert np.squeeze(np.zeros((1, 100))).ndim == 1, 'degenerate 2D -> 1D'
print('PASS: squeeze behaviour correct')
"
```
Expected: PASS

- [ ] **Step 3: Run existing tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add src/nc2cog/processor.py
git commit -m "fix: squeeze non-spatial singleton dimensions before band write

Apply np.squeeze() after reading variable data to collapse size-1
dimensions (e.g. z=1) into the 2D raster expected by GDAL WriteArray.
Adds a dimension guard that raises a clear error if squeeze produces
non-2D data.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: End-to-end verification with the GALE file

- [ ] **Step 1: Convert the GALE file that originally failed**

Run:
```bash
nc2cog "/Users/sam/Works/风云公司/42_一体机/发布产物样例/风雷下游三产品/GALE_202506201400_00_30.nc" /tmp/nc2cog_test_output/
```
Expected:
- `z` variable is NOT listed in the "converting variables" line
- `gale_probability`, `max_wind_speed`, `wind_direction` all succeed
- `Successful: 3, Failed: 0`

- [ ] **Step 2: Verify output files**

Run:
```bash
gdalinfo /tmp/nc2cog_test_output/gale_probability.tif | head -20
gdalinfo /tmp/nc2cog_test_output/max_wind_speed.tif | head -20
gdalinfo /tmp/nc2cog_test_output/wind_direction.tif | head -20
```
Expected: Each shows valid GeoTIFF with 1 band, 100x100 size

- [ ] **Step 3: Verify standard file still works**

Run:
```bash
nc2cog tests/data/sample.nc /tmp/nc2cog_test_output/ --overwrite
```
Expected: Successful conversion of `temperature` variable

- [ ] **Step 4: Cleanup**

```bash
rm -rf /tmp/nc2cog_test_output/
```
