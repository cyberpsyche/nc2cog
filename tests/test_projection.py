"""Tests for projection functionality."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.nc2cog.processor import ProcessingEngine
from src.nc2cog.config import ConfigManager


def test_projection_engine_initialization():
    """Test that ProcessingEngine properly initializes with projection parameters"""
    config_manager = ConfigManager()
    config_manager.config['projection'] = {
        'source': 'EPSG:4326',
        'target': 'EPSG:3857'
    }

    engine = ProcessingEngine(config_manager)

    # Verify that projection attributes are set correctly
    assert engine.source_projection == 'EPSG:4326'
    assert engine.target_projection == 'EPSG:3857'


def test_projection_engine_with_only_target():
    """Test that ProcessingEngine handles only target projection"""
    config_manager = ConfigManager()
    config_manager.config['projection'] = {
        'target': 'EPSG:3857'
    }

    engine = ProcessingEngine(config_manager)

    # Source should be None when not specified
    assert engine.source_projection is None
    assert engine.target_projection == 'EPSG:3857'


def test_projection_engine_without_projections():
    """Test that ProcessingEngine works without projection settings"""
    config_manager = ConfigManager()

    engine = ProcessingEngine(config_manager)

    # Both should be None when not specified
    assert engine.source_projection is None
    assert engine.target_projection is None