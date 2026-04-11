"""Processing engine for netCDF to COG TIFF converter."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from .logger import setup_logger
from .errors import ConversionError, ValidationError
from .config import ConfigManager


# Try to import GDAL, but handle the case where it's not available
try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
except ImportError as e:
    print(f"GDAL import error: {e}", file=sys.stderr)
    gdal = None
    osr = None
    GDAL_AVAILABLE = False
except OSError as e:
    print(f"GDAL shared library error: {e}", file=sys.stderr)
    gdal = None
    osr = None
    GDAL_AVAILABLE = False
except Exception as e:
    print(f"Unexpected GDAL error during import: {e}", file=sys.stderr)
    gdal = None
    osr = None
    GDAL_AVAILABLE = False

# Initialize GDAL exceptions for better error handling if GDAL is available
if GDAL_AVAILABLE:
    gdal.UseExceptions()


class ProcessingEngine:
    """Core processing engine for converting netCDF to COG TIFF."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize processing engine.

        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.logger = setup_logger()

    def convert_file(self, input_file: Path, output_file: Path) -> bool:
        """
        Convert a single netCDF file to COG TIFF.

        Args:
            input_file: Path to input netCDF file
            output_file: Path to output COG TIFF file

        Returns:
            True if conversion was successful, False otherwise
        """
        if not GDAL_AVAILABLE:
            raise ConversionError("GDAL is not available. Please install GDAL with Python bindings.")

        try:
            self.logger.info(f"Starting conversion: {input_file} -> {output_file}")

            # Create output directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Open the netCDF file with GDAL
            dataset = gdal.Open(str(input_file))
            if dataset is None:
                raise ConversionError(f"Failed to open netCDF file: {input_file}")

            # Get configuration parameters
            compression = self.config.get('compression', 'deflate')
            zlevel = self.config.get('zlevel', 6)
            tile_size = self.config.get('tile_size', [512, 512])
            block_size = self.config.get('block_size', [256, 256])
            overviews = self.config.get('overviews', {})

            # Prepare creation options for intermediate GeoTIFF
            # Remove COPY_SRC_OVERVIEWS=YES to avoid conflicts with manual overview building
            creation_options = [
                f'COMPRESS={compression.upper()}',
                f'TILED=YES',
                f'TILEWIDTH={tile_size[0]}',
                f'TILEHEIGHT={tile_size[1]}',
                f'BLOCKXSIZE={block_size[0]}',
                f'BLOCKYSIZE={block_size[1]}',
                'BIGTIFF=IF_SAFER'
            ]

            # Create COG using temporary file to avoid memory issues
            temp_output = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
            temp_output.close()
            temp_path = Path(temp_output.name)

            try:
                # Translate to GeoTIFF first (with specified options)
                gdal.Translate(
                    str(temp_path),
                    dataset,
                    format='GTiff',
                    creationOptions=creation_options,
                    outputType=gdal.GDT_Float32  # Adjust as needed based on input data
                )

                # Build overviews if specified
                if overviews:
                    temp_dataset = gdal.Open(str(temp_path), gdal.GA_Update)
                    if temp_dataset is not None:
                        resampling = overviews.get('resampling', 'nearest')
                        levels = overviews.get('levels', [2, 4, 8, 16])

                        # Build overview pyramid
                        temp_dataset.BuildOverviews(resampling, levels)
                        temp_dataset = None  # Properly close dataset to release file handle

                # Convert to COG format - handle overviews properly in COG creation
                cog_creation_options = [
                    f'COMPRESS={compression.upper()}',
                    f'BLOCKSIZE={block_size[0]}',
                    f'BIGTIFF=IF_SAFER'
                ]

                # If overviews were built, make sure they are handled properly in COG
                if overviews:
                    # Add overviews to COG creation options
                    cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')

                gdal.Translate(
                    str(output_file),
                    str(temp_path),
                    format='COG',
                    creationOptions=cog_creation_options
                )

                self.logger.info(f"Successfully converted: {input_file}")
                return True

            finally:
                # Clean up temporary file
                if temp_path.exists():
                    os.unlink(temp_path)

        except Exception as e:
            self.logger.error(f"Conversion failed for {input_file}: {str(e)}")
            raise ConversionError(f"Conversion failed for {input_file}: {str(e)}")

    def validate_input(self, input_file: Path) -> bool:
        """
        Validate that the input file is a valid netCDF file.

        Args:
            input_file: Path to input file to validate

        Returns:
            True if the file is valid, False otherwise
        """
        if not GDAL_AVAILABLE:
            raise ValidationError("GDAL is not available. Cannot validate netCDF files.")

        try:
            # Try to open the file with GDAL to see if it's readable
            dataset = gdal.Open(str(input_file))
            if dataset is None:
                raise ValidationError(f"Cannot open file as netCDF: {input_file}")

            # Check that it has at least one raster band
            if dataset.RasterCount == 0:
                raise ValidationError(f"No raster bands found in netCDF: {input_file}")

            # Close the dataset
            dataset = None

            return True

        except Exception as e:
            raise ValidationError(f"Validation failed for {input_file}: {str(e)}")

    def calculate_memory_usage(self, input_file: Path) -> int:
        """
        Calculate approximate memory usage for processing the input file.

        Args:
            input_file: Path to input file

        Returns:
            Approximate memory usage in bytes
        """
        if not GDAL_AVAILABLE:
            self.logger.warning("GDAL is not available. Cannot calculate memory usage.")
            return 0

        try:
            dataset = gdal.Open(str(input_file))
            if dataset is None:
                return 0

            # Calculate based on dimensions and data type
            width = dataset.RasterXSize
            height = dataset.RasterYSize
            bands = dataset.RasterCount

            # Get the data type of the first band
            data_type = dataset.GetRasterBand(1).DataType
            dtype_size = gdal.GetDataTypeSize(data_type) // 8  # Convert bits to bytes

            # Calculate memory usage (with some overhead)
            memory_usage = width * height * bands * dtype_size * 3  # 3x for processing overhead
            dataset = None

            return memory_usage

        except Exception:
            return 0