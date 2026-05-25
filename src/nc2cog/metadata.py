"""Metadata collector and writer for COG TIFF files."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import numpy as np

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

from .errors import ConversionError, ValidationError
from .logger import setup_logger

logger = setup_logger()

if GDAL_AVAILABLE:
    gdal.UseExceptions()

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

        if not nc_file.exists():
            raise ValidationError(f"NetCDF file not found: {nc_file}")

        if not temp_tiff_path.exists():
            raise ValidationError(f"Intermediate GeoTIFF not found: {temp_tiff_path}")

        logger.info(f"Collecting metadata from {temp_tiff_path}")

        # Read from the intermediate GeoTIFF
        ds = gdal.Open(str(temp_tiff_path))
        if ds is None:
            raise ConversionError(f"Cannot open intermediate GeoTIFF: {temp_tiff_path}")

        gt = ds.GetGeoTransform()
        projection = ds.GetProjection()
        width = ds.RasterXSize
        height = ds.RasterYSize
        band_count = ds.RasterCount

        if band_count == 0:
            ds = None
            raise ConversionError(
                f"No raster bands in intermediate GeoTIFF: {temp_tiff_path}"
            )

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

        # NODATA — read from first band, fallback to -9999.0
        first_band = ds.GetRasterBand(1)
        nodata = first_band.GetNoDataValue()
        if nodata is None:
            nodata = -9999.0
        metadata[FIELD_NODATA] = f"{nodata}"

        ds.FlushCache()
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
        raise ConversionError("GDAL is required to write metadata")

    ds = gdal.Open(str(cog_path), gdal.GA_Update)
    if ds is None:
        raise ConversionError(f"Cannot open COG file for metadata update: {cog_path}")

    ds.SetMetadata(metadata)
    ds.FlushCache()
    ds = None  # Close and flush
