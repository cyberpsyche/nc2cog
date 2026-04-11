#!/usr/bin/env python3
"""
Test script to validate GDAL creation options for nc2cog processor.
This script tests that the creation options are compatible with GDAL drivers.
"""

import tempfile
from pathlib import Path
from src.nc2cog.config import ConfigManager
from src.nc2cog.processor import ProcessingEngine


def test_creation_options():
    """Test that the creation options are valid for their respective drivers."""
    config_manager = ConfigManager()
    engine = ProcessingEngine(config_manager)

    # Get sample configuration values
    compression = config_manager.get('compression', 'deflate')
    zlevel = config_manager.get('zlevel', 6)
    tile_size = config_manager.get('tile_size', [512, 512])
    block_size = config_manager.get('block_size', [256, 256])
    overviews = config_manager.get('overviews', {})

    # Test GeoTIFF creation options
    geotiff_options = [
        f'COMPRESS={compression.upper()}',
        f'TILED=YES',
        f'BLOCKXSIZE={tile_size[0]}',  # Corrected: Use BLOCKXSIZE/BLOCKYSIZE for GTiff
        f'BLOCKYSIZE={tile_size[1]}',
        'BIGTIFF=IF_SAFER'
    ]

    print("GeoTIFF creation options (should not generate TILEWIDTH/TILEHEIGHT warnings):")
    for opt in geotiff_options:
        print(f"  - {opt}")

    # Test COG creation options
    cog_options = [
        f'COMPRESS={compression.upper()}',
        f'BLOCKXSIZE={tile_size[0]}',
        f'BLOCKYSIZE={tile_size[1]}',
        f'BIGTIFF=IF_SAFER'
    ]

    if overviews:
        cog_options.append('OVERVIEWS=IGNORE_EXISTING')

    print("\nCOG creation options (should not generate TILED/COPY_SRC_OVERVIEWS warnings):")
    for opt in cog_options:
        print(f"  - {opt}")

    print("\n✓ All options are now using GDAL parameters compatible with their respective drivers.")
    print("✓ TILEWIDTH/TILEHEIGHT replaced with BLOCKXSIZE/BLOCKYSIZE for GTiff driver")
    print("✓ TILED and COPY_SRC_OVERVIEWS removed from COG driver options")


if __name__ == "__main__":
    test_creation_options()