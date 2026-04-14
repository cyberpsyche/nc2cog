# User Manual for netCDF to COG TIFF Converter

## Installation

To install the netCDF to COG TIFF converter, make sure you have Python 3.14+ and GDAL installed, then run:

```bash
pip install -e .
```

Or for a development installation:

```bash
pip install -e .
```

## Basic Usage

Convert all netCDF files in a directory to COG TIFF format:

```bash
nc2cog /path/to/input/dir /path/to/output/dir
```

Convert a single file:

```bash
nc2cog /path/to/input/file.nc /path/to/output/directory/
```

## Command Options

- `--config, -c PATH`: Load configuration from a file
- `--compression TYPE`: Compression type (deflate, lzw, jpeg)
- `--tile-size N`: Tile size for COG (default: 512)
- `--overwrite`: Overwrite existing output files
- `--dry-run`: Show what would be processed without doing it
- `--verbose, -v`: Enable verbose logging
- `--resume`: Resume from last processed file
- `--threads N`: Number of parallel processing threads
- `--src-proj TEXT`: Source projection in EPSG format (e.g., EPSG:4326)
- `--dst-proj TEXT`: Target projection in EPSG format (e.g., EPSG:3857)

## Examples

### Convert with custom compression
```bash
nc2cog --compression jpeg /input/dir /output/dir
```

### Process with detailed logging
```bash
nc2cog --verbose /input/dir /output/dir
```

### Perform a dry run
```bash
nc2cog --dry-run /input/dir /output/dir
```

### Resume interrupted processing
```bash
nc2cog --resume /input/dir /output/dir
```

### Projection Transformation Examples

Convert with reprojection from WGS84 to Web Mercator:
```bash
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 /input/file.nc /output/dir/
```

Specify only target projection (source will be detected automatically):
```bash
nc2cog --dst-proj EPSG:3857 /input/file.nc /output/dir/
```

Combine reprojection with other options:
```bash
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 --compression lzw --verbose /input/file.nc /output/dir/
```

## Configuration

You can customize the conversion process using a configuration file in YAML format. For more details, see the [Configuration Guide](configuration_guide.md).