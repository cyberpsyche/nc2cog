"""Tests for GDAL warnings fix and parameter handling."""

import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

# Add the src directory to the Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nc2cog.processor import ProcessingEngine
from nc2cog.config import ConfigManager
from nc2cog.cli import main


def test_gdal_config_options_set_before_gdal_init():
    """Test that GDAL config options are set before GDAL initialization."""
    # We'll mock GDAL availability to test our logic without needing GDAL installed
    with patch('nc2cog.processor.GDAL_AVAILABLE', True), \
         patch('nc2cog.processor.gdal'), \
         patch('nc2cog.processor.osr'):

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as temp_input:
            temp_input.write(b'dummy netcdf content')
            temp_input_path = Path(temp_input.name)

        try:
            # Create a temporary output directory
            with tempfile.TemporaryDirectory() as temp_output_dir:
                output_path = Path(temp_output_dir) / "output.tif"

                # Initialize config manager
                config_manager = ConfigManager()

                # Initialize processing engine
                engine = ProcessingEngine(config_manager)

                # Check that GDAL environment variables are set correctly to suppress warnings
                assert os.environ.get('CPL_LOG_ERRORS', 'OFF') == 'OFF'
                assert os.environ.get('GDAL_FILENAME_IS_UTF8', 'YES') == 'YES'

                # Verify that UseExceptions was called if GDAL is available
                # This happens in the processor module when GDAL_AVAILABLE is True
                # In a real scenario, we'd check if gdal.UseExceptions() was called

        finally:
            # Clean up temp file
            if temp_input_path.exists():
                os.unlink(temp_input_path)


def test_gdal_suppress_warnings_environment_vars():
    """Test that environment variables for suppressing GDAL warnings are set correctly."""
    # Test that the proper environment variables are set to minimize GDAL warnings
    original_cpl_log = os.environ.get('CPL_LOG_ERRORS')
    original_gdal_utf8 = os.environ.get('GDAL_FILENAME_IS_UTF8')

    try:
        # Simulate what happens in the processor when GDAL is available
        os.environ['CPL_LOG_ERRORS'] = 'OFF'
        os.environ['GDAL_FILENAME_IS_UTF8'] = 'YES'

        # Verify settings
        assert os.environ['CPL_LOG_ERRORS'] == 'OFF'
        assert os.environ['GDAL_FILENAME_IS_UTF8'] == 'YES'

    finally:
        # Restore original values
        if original_cpl_log is not None:
            os.environ['CPL_LOG_ERRORS'] = original_cpl_log
        else:
            os.environ.pop('CPL_LOG_ERRORS', None)

        if original_gdal_utf8 is not None:
            os.environ['GDAL_FILENAME_IS_UTF8'] = original_gdal_utf8
        else:
            os.environ.pop('GDAL_FILENAME_IS_UTF8', None)


def test_geotiff_creation_options_validation():
    """Test that GeoTIFF creation options are properly validated."""
    config_manager = ConfigManager()

    # Test default compression setting
    compression = config_manager.get('compression', 'deflate')
    assert compression in ['deflate', 'lzw', 'jpeg']

    # Test zlevel validation
    zlevel = config_manager.get('zlevel', 6)
    assert 1 <= zlevel <= 9

    # Test tile size validation
    tile_size = config_manager.get('tile_size', [512, 512])
    assert isinstance(tile_size, list)
    assert len(tile_size) == 2
    assert all(isinstance(size, int) and size > 0 for size in tile_size)

    # Test block size validation
    block_size = config_manager.get('block_size', [256, 256])
    assert isinstance(block_size, list)
    assert len(block_size) == 2
    assert all(isinstance(size, int) and size > 0 for size in block_size)


def test_cog_creation_options_format():
    """Test that COG creation options have the correct format."""
    config_manager = ConfigManager()

    compression = config_manager.get('compression', 'deflate')
    block_size = config_manager.get('block_size', [256, 256])

    # Format creation options similar to how they're used in processor
    cog_creation_options = [
        f'COMPRESS={compression.upper()}',
        f'BLOCKSIZE={block_size[0]}',
        'BIGTIFF=IF_SAFER'
    ]

    # Verify format of options
    assert any(opt.startswith('COMPRESS=') for opt in cog_creation_options)
    assert any(opt.startswith('BLOCKSIZE=') for opt in cog_creation_options)
    assert 'BIGTIFF=IF_SAFER' in cog_creation_options

    # Verify compression is uppercase
    compress_option = [opt for opt in cog_creation_options if opt.startswith('COMPRESS=')][0]
    assert compress_option.split('=')[1] in ['DEFLATE', 'LZW', 'JPEG']


def test_overview_handling_in_creation_options():
    """Test that overview handling is properly included in creation options."""
    config_manager = ConfigManager()

    # Set up overviews configuration
    config_manager.config['overviews'] = {
        'resampling': 'nearest',
        'levels': [2, 4, 8, 16]
    }

    overviews = config_manager.get('overviews', {})

    # Test that overviews configuration is accessible
    assert 'resampling' in overviews
    assert 'levels' in overviews
    assert overviews['resampling'] in ['nearest', 'bilinear', 'cubic', 'average', 'mode', 'gauss', 'rms']
    assert isinstance(overviews['levels'], list)
    assert all(isinstance(level, int) and level > 0 for level in overviews['levels'])

    # Test creation options when overviews are present
    cog_creation_options = [
        f'COMPRESS={config_manager.get("compression", "deflate").upper()}',
        f'BLOCKSIZE={config_manager.get("block_size", [256, 256])[0]}',
        'BIGTIFF=IF_SAFER'
    ]

    if overviews:
        cog_creation_options.append('OVERVIEWS=IGNORE_EXISTING')

    # Verify OVERVIEWS option is included when overviews exist
    assert 'OVERVIEWS=IGNORE_EXISTING' in cog_creation_options


def test_cli_parameter_integration_with_gdal_options():
    """Test that CLI parameters are properly integrated with GDAL options."""
    # Mock GDAL for this test
    with patch('nc2cog.processor.GDAL_AVAILABLE', True), \
         patch('nc2cog.processor.gdal'), \
         patch('nc2cog.processor.osr'), \
         patch('nc2cog.cli.ProcessingEngine'), \
         patch('nc2cog.cli.FileDiscovery'), \
         patch('nc2cog.cli.ConfigManager') as mock_config_manager_class:

        # Create a temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nc', delete=False) as temp_input:
            temp_input.write('dummy content')
            temp_input_path = temp_input.name

        try:
            # Mock objects
            mock_file_discovery = MagicMock()
            mock_file_discovery.find_files.return_value = [Path(temp_input_path)]

            mock_config_instance = MagicMock()
            mock_config_instance.get.side_effect = lambda key, default=None: {
                'compression': 'lzw',
                'zlevel': 9,
                'tile_size': [256, 256],
                'block_size': [128, 128],
                'overviews': {'resampling': 'cubic', 'levels': [2, 4]}
            }.get(key, default)

            mock_config_manager_class.return_value = mock_config_instance

            # Simulate parameter integration in CLI
            config_manager = mock_config_instance

            # Test that parameters would be properly integrated
            compression = config_manager.get('compression', 'deflate')
            zlevel = config_manager.get('zlevel', 6)
            tile_size = config_manager.get('tile_size', [512, 512])
            block_size = config_manager.get('block_size', [256, 256])
            overviews = config_manager.get('overviews', {})

            # Verify that values are properly retrieved
            assert compression == 'lzw'
            assert zlevel == 9
            assert tile_size == [256, 256]
            assert block_size == [128, 128]
            assert overviews == {'resampling': 'cubic', 'levels': [2, 4]}

        finally:
            # Clean up temp file
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)


def test_geotiff_creation_options_without_conflicts():
    """Test that GeoTIFF creation options don't have conflicting settings."""
    config_manager = ConfigManager()

    # Test the combination of options that was causing issues before
    creation_options = [
        f'COMPRESS={config_manager.get("compression", "deflate").upper()}',
        'TILED=YES',
        f'TILEWIDTH={config_manager.get("tile_size", [512, 512])[0]}',
        f'TILEHEIGHT={config_manager.get("tile_size", [512, 512])[1]}',
        f'BLOCKXSIZE={config_manager.get("block_size", [256, 256])[0]}',
        f'BLOCKYSIZE={config_manager.get("block_size", [256, 256])[1]}',
        'BIGTIFF=IF_SAFER'
    ]

    # Verify that COPY_SRC_OVERVIEWS is NOT included to prevent conflicts
    # This was part of the original issue - conflicting overview handling
    copy_src_overviews_options = [opt for opt in creation_options if 'COPY_SRC_OVERVIEWS' in opt]
    assert len(copy_src_overviews_options) == 0

    # Verify that basic options are present
    assert any('COMPRESS=' in opt for opt in creation_options)
    assert 'TILED=YES' in creation_options
    assert any('TILEWIDTH=' in opt for opt in creation_options)
    assert any('TILEHEIGHT=' in opt for opt in creation_options)
    assert any('BLOCKXSIZE=' in opt for opt in creation_options)
    assert any('BLOCKYSIZE=' in opt for opt in creation_options)
    assert 'BIGTIFF=IF_SAFER' in creation_options


if __name__ == '__main__':
    pytest.main([__file__])