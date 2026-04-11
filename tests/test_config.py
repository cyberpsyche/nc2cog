"""Tests for configuration management."""

import pytest
from pathlib import Path
import tempfile
import yaml
from src.nc2cog.config import ConfigManager, ConfigError


def test_default_config_loading():
    """Test that default config loads correctly."""
    config_manager = ConfigManager()

    # Check that some default values exist
    assert 'compression' in config_manager.config
    assert 'tile_size' in config_manager.config
    assert config_manager.get('compression') == 'deflate'


def test_user_config_override():
    """Test that user config overrides default values."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'compression': 'lzw'}, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)
        assert config_manager.get('compression') == 'lzw'
    finally:
        temp_config_path.unlink()


def test_nested_config_merge():
    """Test that nested config values merge correctly."""
    # Create a temporary config file with nested values
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'overviews': {'resampling': 'cubic'}}, f)
        temp_config_path = Path(f.name)

    try:
        config_manager = ConfigManager(temp_config_path)
        assert config_manager.get('overviews.resampling') == 'cubic'
        # Other overviews values should remain from default
        assert 'levels' in config_manager.get('overviews')
    finally:
        temp_config_path.unlink()


def test_config_validation():
    """Test that config validation works."""
    config_manager = ConfigManager()

    # Valid compression should pass
    config_manager.config['compression'] = 'deflate'
    config_manager.validate()  # Should not raise

    # Invalid compression should fail
    config_manager.config['compression'] = 'invalid'
    with pytest.raises(ConfigError):
        config_manager.validate()


def test_tile_size_validation():
    """Test tile size validation."""
    config_manager = ConfigManager()

    # Valid tile size should pass
    config_manager.config['tile_size'] = [256, 256]
    config_manager.validate()  # Should not raise

    # Invalid tile size should fail
    config_manager.config['tile_size'] = [0, 256]
    with pytest.raises(ConfigError):
        config_manager.validate()

    # Non-list tile size should fail
    config_manager.config['tile_size'] = "not_a_list"
    with pytest.raises(ConfigError):
        config_manager.validate()


def test_block_size_validation():
    """Test block size validation."""
    config_manager = ConfigManager()

    # Valid block size should pass
    config_manager.config['block_size'] = [128, 128]
    config_manager.validate()  # Should not raise

    # Invalid block size should fail
    config_manager.config['block_size'] = [-1, 128]
    with pytest.raises(ConfigError):
        config_manager.validate()


def test_zlevel_validation():
    """Test zlevel validation."""
    config_manager = ConfigManager()

    # Valid zlevel should pass
    config_manager.config['zlevel'] = 6
    config_manager.validate()  # Should not raise

    # Invalid zlevel should fail
    config_manager.config['zlevel'] = 10
    with pytest.raises(ConfigError):
        config_manager.validate()

    # Another invalid zlevel should fail
    config_manager.config['zlevel'] = 0
    with pytest.raises(ConfigError):
        config_manager.validate()