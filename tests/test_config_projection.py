"""Tests for projection functionality in config files."""
import pytest
from pathlib import Path
import tempfile
import yaml
from src.nc2cog.config import ConfigManager, ConfigError


def test_config_projection_loading():
    """Test that projection parameters are loaded correctly from config."""
    # Create a temporary config file with projection settings
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'projection': {
                'source': 'EPSG:4326',
                'target': 'EPSG:3857',
                'resampling_method': 'bilinear'
            }
        }, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)

        # Check that projection values are accessible
        assert config_manager.get('projection.source') == 'EPSG:4326'
        assert config_manager.get('projection.target') == 'EPSG:3857'
        assert config_manager.get('projection.resampling_method') == 'bilinear'
    finally:
        temp_config_path.unlink()


def test_config_projection_validation_success():
    """Test that valid projection parameters pass validation."""
    # Create a temporary config file with valid projection settings
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'projection': {
                'source': 'EPSG:4326',
                'target': 'EPSG:3857',
                'resampling_method': 'bilinear'
            }
        }, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)
        # Validation should not raise an error
        config_manager.validate()
    finally:
        temp_config_path.unlink()


def test_config_invalid_projection_format():
    """Test that invalid projection formats are caught by validation."""
    # Create a temporary config file with invalid projection settings
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'projection': {
                'source': 'INVALID_FORMAT',
                'target': 'EPSG:3857'
            }
        }, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)
        with pytest.raises(ConfigError):
            config_manager.validate()
    finally:
        temp_config_path.unlink()


def test_config_invalid_epsg_code():
    """Test that invalid EPSG codes are caught by validation."""
    # Create a temporary config file with invalid EPSG code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'projection': {
                'source': 'EPSG:INVALID',
                'target': 'EPSG:3857'
            }
        }, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)
        with pytest.raises(ConfigError):
            config_manager.validate()
    finally:
        temp_config_path.unlink()


def test_config_missing_epsg_part():
    """Test that malformed EPSG codes are caught by validation."""
    # Create a temporary config file with malformed EPSG code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'projection': {
                'source': 'EPSG:',
                'target': 'EPSG:3857'
            }
        }, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)
        with pytest.raises(ConfigError):
            config_manager.validate()
    finally:
        temp_config_path.unlink()