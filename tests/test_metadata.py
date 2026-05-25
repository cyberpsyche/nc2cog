"""Tests for metadata collection and writing."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

TEST_DATA_DIR = Path(__file__).parent / "data"
SAMPLE_NC = TEST_DATA_DIR / "sample.nc"


class TestMetadataCollectorConfig:
    """Test MetadataCollector reads config correctly."""

    def test_default_metadata_config(self):
        """Default config should have metadata section with expected keys."""
        from nc2cog.config import ConfigManager
        cm = ConfigManager()
        assert cm.get('metadata.source', None) == '' or cm.get('metadata.source') is None
        assert cm.get('metadata.offset', 0.0) == 0.0
        assert cm.get('metadata.scale', 1.0) == 1.0

    def test_metadata_source_override(self):
        """Config should accept metadata.source override."""
        from nc2cog.config import ConfigManager
        import yaml, tempfile, os
        config_data = {'metadata': {'source': 'My Satellite'}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            f.flush()
            cm = ConfigManager(config_path=Path(f.name))
        assert cm.get('metadata.source') == 'My Satellite'
        os.unlink(f.name)


@pytest.mark.skipif(not SAMPLE_NC.exists(), reason="Test netCDF not found")
class TestMetadataCollectorIntegration:
    """Integration tests requiring a real netCDF file."""

    def _make_mock_config(self, **overrides):
        """Create a mock ConfigManager with metadata defaults."""
        mock = MagicMock()
        mock.get.side_effect = lambda key, default=None: {
            'metadata.source': overrides.get('source', ''),
            'metadata.offset': overrides.get('offset', 0.0),
            'metadata.scale': overrides.get('scale', 1.0),
            'metadata.unit': overrides.get('unit', ''),
            'compression': 'deflate',
            'projection.target': None,
        }.get(key, default)
        return mock

    def test_extract_source_from_nc(self):
        """Source should be extracted from netCDF global attributes."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config())
        source = collector._extract_source(SAMPLE_NC, None)
        assert source == "Test Satellite"

    def test_extract_unit_from_variable(self):
        """Unit should be extracted from netCDF variable attributes."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config())
        unit = collector._extract_unit(SAMPLE_NC, 'temperature')
        assert unit == "K"

    def test_fallback_source_when_no_nc_attr(self):
        """Should use config fallback when netCDF has no source attribute."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config(source='Fallback Source'))
        source = collector._extract_source(SAMPLE_NC, None)
        # netCDF has 'source' attr, so it should be used, not fallback
        assert source == "Test Satellite"

    def test_fallback_unit_when_no_var_attr(self):
        """Should use config fallback when variable has no units attribute."""
        from nc2cog.metadata import MetadataCollector
        collector = MetadataCollector(self._make_mock_config(unit='fallback_unit'))
        # 'temperature' has units, so it should be used
        unit = collector._extract_unit(SAMPLE_NC, 'temperature')
        assert unit == "K"
        # A variable without units would use fallback
        unit = collector._extract_unit(SAMPLE_NC, 'nonexistent_var')
        assert unit == 'fallback_unit'
