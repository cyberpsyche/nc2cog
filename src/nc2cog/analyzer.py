"""Analyzer for netCDF file structure and subdatasets."""

from pathlib import Path
from typing import List, Dict, Optional

# Coordinate variables to exclude from data variables
_COORD_NAMES = frozenset({
    'lat', 'lon', 'latitude', 'longitude', 'time', 'crs',
    'x', 'y', 'spatial_ref', 'nav_lat', 'nav_lon',
})

# Try to import netCDF4
try:
    import netCDF4
    NETCDF4_AVAILABLE = True
except ImportError:
    NETCDF4_AVAILABLE = False


class NCAnalyzer:
    """Analyzes netCDF files for variable and dimension structure."""

    def __init__(self, input_file: Path):
        """
        Initialize analyzer.

        Args:
            input_file: Path to netCDF file
        """
        self.input_file = Path(input_file)

    def get_subdatasets(self) -> List[str]:
        """
        Get GDAL subdataset paths for this netCDF file.

        Returns:
            List of subdataset paths. Empty list means the file is
            directly readable as a 2D raster (no subdatasets).
        """
        from osgeo import gdal
        ds = gdal.Open(str(self.input_file))
        if ds is None:
            return []

        subdatasets = ds.GetMetadata('SUBDATASETS')
        result = []
        for key, value in subdatasets.items():
            if key.endswith('_NAME'):
                result.append(value)
        return result

    def get_data_variables(self) -> List[str]:
        """
        Get list of data variable names, excluding coordinate variables.

        Returns:
            List of data variable names
        """
        if not NETCDF4_AVAILABLE:
            raise ImportError(
                "netCDF4 is required for multi-dimensional NC files. "
                "Install it with: pip install netCDF4"
            )

        nc = netCDF4.Dataset(str(self.input_file), 'r')
        try:
            # Get all variable names that have >1 dimension (data variables)
            # and exclude known coordinate variables
            data_vars = []
            for name in nc.variables:
                if name.lower() in _COORD_NAMES:
                    continue
                var = nc.variables[name]
                # Must be at least 1D and not a scalar metadata variable
                if var.ndim >= 1 and len(var.dimensions) >= 1:
                    data_vars.append(name)
            return sorted(data_vars)
        finally:
            nc.close()

    def analyze_subdataset(self, subdataset_path: str) -> Dict:
        """
        Analyze a GDAL subdataset to extract dimension info.

        Args:
            subdataset_path: GDAL subdataset path

        Returns:
            Dict with keys: name, dims, shape, dtype, time_count, time_units
        """
        from osgeo import gdal
        ds = gdal.Open(subdataset_path)
        if ds is None:
            raise ValueError(f"Cannot open subdataset: {subdataset_path}")

        # Extract variable name from subdataset path
        # Format: NETCDF:"file.nc":VARNAME
        name = subdataset_path.rsplit(':', 1)[-1]

        info = {
            'name': name,
            'width': ds.RasterXSize,
            'height': ds.RasterYSize,
            'bands': ds.RasterCount,
            'dtype': gdal.GetDataTypeName(ds.GetRasterBand(1).DataType),
            'gdal_dtype': ds.GetRasterBand(1).DataType,
        }

        # Try to get time info from netCDF4
        if NETCDF4_AVAILABLE:
            try:
                nc = netCDF4.Dataset(str(self.input_file), 'r')
                if name in nc.variables:
                    var = nc.variables[name]
                    info['dims'] = list(var.dimensions)
                    info['shape'] = list(var.shape)

                    # Find time dimension
                    for dim_name in var.dimensions:
                        if dim_name.lower() in ('time', 't'):
                            if dim_name in nc.variables:
                                time_var = nc.variables[dim_name]
                                info['time_count'] = len(time_var)
                                info['time_units'] = getattr(time_var, 'units', None)
                                if hasattr(time_var, '__getitem__'):
                                    info['time_values'] = time_var[:]
                nc.close()
            except Exception:
                pass

        return info

    def get_time_descriptions(self, variable_name: str) -> List[str]:
        """
        Get human-readable time descriptions for a variable.

        Args:
            variable_name: Name of the variable

        Returns:
            List of time step descriptions
        """
        if not NETCDF4_AVAILABLE:
            return []

        try:
            from datetime import datetime, timedelta
            nc = netCDF4.Dataset(str(self.input_file), 'r')
            try:
                if variable_name not in nc.variables:
                    return []

                var = nc.variables[variable_name]
                time_dim_name = None
                for dim_name in var.dimensions:
                    if dim_name.lower() in ('time', 't'):
                        time_dim_name = dim_name
                        break

                if time_dim_name is None or time_dim_name not in nc.variables:
                    return [f"step_{i}" for i in range(var.shape[0])]

                time_var = nc.variables[time_dim_name]
                time_units = getattr(time_var, 'units', None)
                times = time_var[:]

                descriptions = []
                if time_units:
                    # Parse CF time units like "minutes since 2025-11-13T06:30:00"
                    try:
                        base_str = time_units.split(' since ')[1].strip()
                        for i, t in enumerate(times):
                            # netCDF4.num2date handles the conversion
                            dt = netCDF4.num2date(t, time_units)
                            descriptions.append(f"time={i}, {dt.isoformat()}")
                    except Exception:
                        descriptions = [f"time={i}" for i in range(len(times))]
                else:
                    descriptions = [f"time={i}" for i in range(len(times))]

                return descriptions
            finally:
                nc.close()
        except Exception:
            return []
