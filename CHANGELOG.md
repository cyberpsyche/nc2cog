# Changelog

All notable changes to the nc2cog project will be documented in this file.

## [Unreleased] - YYYY-MM-DD

### Added
- `--overview-levels` CLI parameter to control pyramid structure
- GDAL exception handling with `gdal.UseExceptions()`
- Comprehensive documentation in docs/ directory
- GDAL warning elimination through driver-specific parameters

### Changed
- Fixed GTiff driver parameters to use `BLOCKXSIZE`/`BLOCKYSIZE` instead of `TILEWIDTH`/`TILEHEIGHT`
- Fixed COG driver parameters to use `BLOCKSIZE` instead of `BLOCKXSIZE`/`BLOCKYSIZE`
- Updated `--resampling` parameter to support additional methods: `gauss` and `rms`
- Enhanced README with comprehensive usage examples
- Optimized overview generation to prevent GDAL conflicts

### Fixed
- Removed GDAL warnings for GTiff driver regarding unsupported parameters
- Removed GDAL warnings for COG driver regarding unsupported parameters
- Fixed conflicts between `COPY_SRC_OVERVIEWS` and manual overview building
- Resolved issues with `TILED=YES` and `COPY_SRC_OVERVIEWS` for COG driver
- Corrected GDAL parameter usage based on driver capabilities

### Security
- N/A

## [1.0.0] - 2026-04-11

### Added
- Initial release of netCDF to COG converter
- Basic CLI functionality with support for compression settings
- Configuration file support (YAML)
- Support for multi-threaded processing
- Resume capability for interrupted conversions
- Overview/resampling controls

### Changed
- N/A

### Fixed
- N/A

### Security
- N/A