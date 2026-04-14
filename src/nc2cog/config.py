"""Configuration management for netCDF to COG TIFF converter."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .errors import ConfigError


class ConfigManager:
    """Manages configuration for the netCDF to COG TIFF converter."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to config file
        """
        self.default_config_path = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
        self.user_config_path = config_path

        # Load and merge configurations
        self._config = self._load_default_config()
        if config_path:
            user_config = self._load_user_config(config_path)
            self._config = self._merge_configs(self._config, user_config)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from file."""
        if not self.default_config_path.exists():
            raise ConfigError(f"Default configuration file not found: {self.default_config_path}")

        with open(self.default_config_path, 'r') as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in default config: {e}")

    def _load_user_config(self, config_path: Path) -> Dict[str, Any]:
        """Load user configuration from file."""
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in config file: {config_path}: {e}")

    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config into default config."""
        result = default.copy()

        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    @property
    def config(self) -> Dict[str, Any]:
        """Get the merged configuration."""
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key using dot notation (e.g., 'processing.compression')
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def validate(self) -> None:
        """Validate configuration values."""
        # Compression type validation
        compression = self.get('compression', 'deflate')
        valid_compressions = ['deflate', 'lzw', 'jpeg']
        if compression not in valid_compressions:
            raise ConfigError(f"Invalid compression type: {compression}. Valid options: {valid_compressions}")

        # Tile size validation
        tile_size = self.get('tile_size', [512, 512])
        if not isinstance(tile_size, list) or len(tile_size) != 2:
            raise ConfigError(f"Invalid tile_size: {tile_size}. Must be a list of two integers.")

        for size in tile_size:
            if not isinstance(size, int) or size <= 0:
                raise ConfigError(f"Invalid tile size: {size}. Must be a positive integer.")

        # Block size validation
        block_size = self.get('block_size', [256, 256])
        if not isinstance(block_size, list) or len(block_size) != 2:
            raise ConfigError(f"Invalid block_size: {block_size}. Must be a list of two integers.")

        for size in block_size:
            if not isinstance(size, int) or size <= 0:
                raise ConfigError(f"Invalid block size: {size}. Must be a positive integer.")

        # Z-level validation
        zlevel = self.get('zlevel', 6)
        if not isinstance(zlevel, int) or zlevel < 1 or zlevel > 9:
            raise ConfigError(f"Invalid zlevel: {zlevel}. Must be an integer between 1 and 9.")

        # Overviews resampling validation
        resampling = self.get('overviews.resampling', 'nearest')
        valid_resampling_methods = ['nearest', 'bilinear', 'cubic', 'cubicspline', 'lanczos', 'average', 'mode']
        if resampling not in valid_resampling_methods:
            raise ConfigError(f"Invalid resampling method: {resampling}. Valid options: {valid_resampling_methods}")

        # Projection parameters validation
        source_projection = self.get('projection.source', None)
        target_projection = self.get('projection.target', None)
        resampling_method = self.get('projection.resampling_method', 'nearest')

        if source_projection is not None:
            # Validate source projection format (expecting EPSG:XXXX format)
            if not isinstance(source_projection, str) or not source_projection.upper().startswith('EPSG:'):
                raise ConfigError(f"Invalid source projection format: {source_projection}. Expected format: 'EPSG:XXXX'")

            # Validate EPSG code structure (should be EPSG:number)
            try:
                epsg_code = source_projection.split(':')[1]
                int(epsg_code)  # Verify it's a valid integer
            except (IndexError, ValueError):
                raise ConfigError(f"Invalid source EPSG code: {source_projection}. Expected format: 'EPSG:XXXX' where XXXX is a number")

        if target_projection is not None:
            # Validate target projection format (expecting EPSG:XXXX format)
            if not isinstance(target_projection, str) or not target_projection.upper().startswith('EPSG:'):
                raise ConfigError(f"Invalid target projection format: {target_projection}. Expected format: 'EPSG:XXXX'")

            # Validate EPSG code structure (should be EPSG:number)
            try:
                epsg_code = target_projection.split(':')[1]
                int(epsg_code)  # Verify it's a valid integer
            except (IndexError, ValueError):
                raise ConfigError(f"Invalid target EPSG code: {target_projection}. Expected format: 'EPSG:XXXX' where XXXX is a number")

        # Validate reprojection resampling method
        valid_reprojection_methods = ['nearest', 'bilinear', 'cubic', 'cubicspline', 'lanczos', 'average', 'mode', 'max', 'min', 'med', 'q1', 'q3']
        if resampling_method not in valid_reprojection_methods:
            raise ConfigError(f"Invalid reprojection resampling method: {resampling_method}. Valid options: {valid_reprojection_methods}")