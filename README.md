# netCDF to COG TIFF Converter

A command-line tool for batch converting netCDF files to Cloud-Optimized GeoTIFF format.

## Installation

```bash
pip install -e .
```

## Usage

```bash
nc2cog /path/to/input/dir /path/to/output/dir
```

### Advanced Options

The tool supports several CLI parameters for fine-tuning the conversion process:

- `--zlevel`: Compression level (1-9) for deflate compression, where higher values mean better compression but slower processing
- `--block-size`: Block size for compression (default: 256), affecting memory usage and compression efficiency
- `--tile-size`: Tile size for COG (default: 512), affecting performance and memory usage during access
- `--resampling`: Resampling method for overviews (default: nearest), options include nearest, bilinear, cubic, average, mode, gauss, and rms

Examples:
```bash
# High compression level
nc2cog --compression deflate --zlevel 9 /path/to/input /path/to/output

# Custom block and tile sizes for performance tuning  
nc2cog --block-size 512 --tile-size 1024 /path/to/input /path/to/output

# High-quality overview resampling
nc2cog --resampling cubic /path/to/input /path/to/output

# Combine multiple parameters
nc2cog --zlevel 8 --tile-size 1024 --block-size 512 --resampling cubic /path/to/input /path/to/output
```

For detailed usage, see the [User Manual](docs/user_manual.md).