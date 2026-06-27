# Fix: Support netCDF files with extra singleton dimensions (e.g. z=1)

**Date**: 2026-06-27
**Status**: Approved
**Scope**: `analyzer.py`, `metadata.py`, `processor.py`

## Problem

When converting netCDF files with dimensions beyond the standard `(time, y, x)` —
specifically `(time, z, y, x)` where `z=1` — two bugs prevent successful conversion:

1. **Coordinate variable `z` incorrectly included as data variable**: The
   coordinate-variable exclusion list `_COORD_NAMES` does not contain `'z'`, so
   `z(z=1)` is treated as a data variable. Its single spatial dimension triggers
   "must have at least 2 spatial dimensions".

2. **4D data not squeezed before band write**: Variables like
   `gale_probability(time=1, z=1, y=100, x=100)` are read as 4D arrays `(1,1,100,100)`.
   GDAL's `WriteArray` expects 2D, producing "expected array of dim 2".

Both bugs stem from the implicit assumption that data variables are at most 3D
`(time, y, x)`.

## Design

### Change 1: Extract shared `_COORD_NAMES` constant

**File**: `analyzer.py` — rename `_COORD_NAMES` → `COORD_NAMES` (drop underscore prefix,
now a shared package constant).

**File**: `metadata.py` — delete the local `_COORD_NAMES` definition. Import from
`analyzer.py` instead:

```python
from .analyzer import COORD_NAMES
```

Update the one reference in `metadata.py:_extract_unit()` from `_COORD_NAMES` to `COORD_NAMES`.

Removes the duplication that allowed the two copies to diverge.

### Change 2: CF-convention coordinate variable detection

**File**: `analyzer.py` — `NCAnalyzer.get_data_variables()`

After the existing hardcoded-name check, add a CF-1.8 convention check: a variable
whose single dimension has the same name as the variable itself is a coordinate
variable and must be excluded.

```python
if len(var.dimensions) == 1 and var.dimensions[0] == name:
    continue
```

This handles `z(z)`, `height(height)`, `depth(depth)`, `pressure(pressure)`,
`level(level)`, and any future CF-compliant coordinate variable without
maintaining an ever-growing hardcoded list.

The hardcoded `COORD_NAMES` set is retained for cases where the variable name
differs from its dimension name (e.g. `latitude(lat)`, `longitude(lon)`).

### Change 3: Squeeze non-spatial singleton dimensions

**File**: `processor.py` — `ProcessingEngine._convert_variable_to_cog()`

After reading data in both the `time_steps == 1` and `time_steps > 1` branches,
apply `np.squeeze()` to collapse all size-1 dimensions. Add a safety check
ensuring the result is 2D:

```python
data = np.squeeze(data)
if data.ndim != 2:
    raise ConversionError(
        f"Expected 2D data after squeezing, got {data.ndim}D "
        f"with shape {data.shape} for variable {var_name}"
    )
```

This correctly handles:

| Input shape | Source | Squeezed | Result |
|---|---|---|---|
| `(100, 100)` | 2D variable, no time | `(100, 100)` | unchanged |
| `(1, 100, 100)` | `(time=1, y, x)` var[:] | `(100, 100)` | correct |
| `(1, 1, 100, 100)` | `(time=1, z=1, y, x)` var[:] | `(100, 100)` | correct |
| `(1, 100, 100)` | `(time=N, z=1, y, x)` slice | `(100, 100)` | correct |
| `(1, 100)` | degenerate (1 spatial dim) | `(100,)` | clear error |

## Backward Compatibility

All three changes are **behaviour-preserving** for standard `(time, y, x)` files:

- **Change 1**: Pure deduplication; `_COORD_NAMES` values are identical.
- **Change 2**: `time(time)`, `x(x)`, `y(y)` are already excluded by hardcoded
  names. CF check is additive — it only excludes variables that _should_ have
  been excluded but weren't.
- **Change 3**: `np.squeeze` on an already-2D array `(100, 100)` is a no-op.
  On `(1, 100, 100)` (current behaviour for `time=1` files) it safely reduces
  to `(100, 100)`, which is what `WriteArray` expected all along.

## Files Changed

| File | Change |
|---|---|
| `src/nc2cog/analyzer.py` | Rename `_COORD_NAMES` → `COORD_NAMES`; add CF convention check in `get_data_variables()` |
| `src/nc2cog/metadata.py` | Import `COORD_NAMES` from analyzer; delete local copy |
| `src/nc2cog/processor.py` | `np.squeeze()` + dimension guard in `_convert_variable_to_cog` |

## Testing

Manual verification steps:

1. Convert the GALE file that triggered the bug — all 3 data variables should succeed, `z` should be excluded.
2. Convert `tests/data/sample.nc` (standard `(time, lat, lon)` structure) — behaviour unchanged.
3. Convert a single-timestep file (`time=1`) — squeeze path exercised.
4. Convert a multi-timestep file (`time>1`) — slice path exercised.
