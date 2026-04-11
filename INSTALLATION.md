# Installation Guide for nc2cog

## Overview

nc2cog is a command-line tool for converting netCDF files to Cloud-Optimized GeoTIFF (COG) format with advanced compression and performance settings.

## Prerequisites

### System Requirements
- Python 3.7 or higher
- GDAL library with Python bindings
- Sufficient disk space for temporary files during conversion
- Appropriate permissions for input/output directories

### GDAL Installation Solutions

The netCDF to COG TIFF converter tool has been successfully implemented with proper error handling for GDAL availability. Here's how to properly install GDAL on different systems:

#### For macOS (with Homebrew):

```bash
# Install GDAL via Homebrew
brew install gdal

# Then install Python bindings
pip install GDAL==$(gdal-config --version)
```

#### For macOS (with Conda - Alternative approach):

```bash
# Create a new conda environment with GDAL
conda create -n nc2cog python=3.11 gdal
conda activate nc2cog
pip install -e /path/to/nc_cogtiff
```

#### For Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)
```

#### For other systems:

Please follow the official GDAL installation guide: https://gdal.org/download.html

## Installing nc2cog

```bash
# Clone the repository
git clone <repository-url>
cd nc2cog

# Install Python dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Using the Tool

Once GDAL is properly installed, you can use the tool as follows:

### Basic Usage
```bash
# Convert a single file
nc2cog input.nc output/

# Convert all netCDF files in a directory
nc2cog input_dir/ output/
```

### Advanced Usage
```bash
# With compression settings
nc2cog --compression deflate --zlevel 9 /path/to/input/dir /path/to/output/dir

# With performance tuning
nc2cog --tile-size 1024 --block-size 512 /path/to/input/dir /path/to/output/dir

# With overview/Pyramid controls
nc2cog --resampling cubic --overview-levels 2,4,8,16 /path/to/input/dir /path/to/output/dir

# With parallel processing
nc2cog --threads 4 /path/to/input/dir /path/to/output/dir

# With configuration file
nc2cog --config /path/to/config.yaml /path/to/input/dir /path/to/output/dir

# With verbose logging
nc2cog -v --tile-size 1024 /path/to/input/dir /path/to/output/dir

# Combine multiple parameters
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 8 \
  --tile-size 1024 \
  --block-size 512 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

## Available Command Line Parameters

### Core Parameters
- `input_path`: Input file path (file or directory)
- `output_path`: Output directory path

### Configuration Parameters
- `--config, -c`: Path to configuration file
- `--compression`: Compression type (deflate, lzw, jpeg)
- `--zlevel`: Compression level (1-9, for deflate only)

### Performance Parameters
- `--tile-size`: Tile size for COG (default: 512)
- `--block-size`: Block size for compression (default: 256)

### Overview/Pyramid Parameters
- `--resampling`: Resampling method (nearest, bilinear, cubic, average, mode, gauss, rms)
- `--overview-levels`: Overview levels as comma-separated values (default: 2,4,8,16)

### Control Parameters
- `--overwrite`: Overwrite existing output files
- `--dry-run`: Show what would be processed without doing it
- `--verbose, -v`: Enable verbose logging
- `--resume`: Resume from last processed file
- `--threads`: Number of parallel processing threads (default: 1)

## Configuration File Example

Create `config.yaml`:

```yaml
# Processing parameters
compression: "deflate"
zlevel: 6
tile_size: [512, 512]
block_size: [256, 256]

# Output options
overviews:
  resampling: "nearest"
  levels: [2, 4, 8, 16]

# Processing control
overwrite: false
skip_errors: true
```

Use with: `nc2cog --config config.yaml input.nc output/`

## Verification

To verify that GDAL is working properly:

```bash
# Test GDAL installation
gdalinfo --version

# Verify Python GDAL binding
python -c "from osgeo import gdal; print(gdal.__version__)"

# Test the nc2cog tool
nc2cog --help
```

## GDAL Optimization Features

The tool includes several GDAL optimizations:
- Driver-specific parameter validation to eliminate warnings
- Proper parameter usage for GTiff and COG drivers
- Optimized overview generation to avoid conflicts
- Enhanced error handling and logging

## Production Deployment Notes

The tool is designed for production use with:

- Proper error handling for missing GDAL
- Comprehensive logging
- Configuration management
- Batch processing capabilities
- Resume functionality for interrupted jobs
- Memory usage estimation
- File discovery with pattern matching
- GDAL warnings elimination
- Multi-threaded processing support

The tool gracefully handles GDAL unavailability by raising appropriate errors rather than crashing, ensuring production stability.