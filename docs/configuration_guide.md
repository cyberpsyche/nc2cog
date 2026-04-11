# Configuration Guide for netCDF to COG TIFF Converter

## Overview

The converter can be customized using a YAML configuration file. You can either provide a configuration file via the `--config` option or modify the default configuration.

## Configuration Parameters

### Processing Parameters

- `compression`: Compression algorithm to use. Options: `deflate`, `lzw`, `jpeg`
- `zlevel`: Compression level (1-9), only used with deflate compression
- `tile_size`: Array with [width, height] of tiles in pixels
- `block_size`: Array with [width, height] of blocks in pixels

### Output Options

- `overviews.resampling`: Resampling method for overviews. Options: `nearest`, `average`, `gauss`, `cubic`, `lanczos`
- `overviews.levels`: Array of overview levels to generate (e.g., [2, 4, 8, 16])

### Processing Control

- `overwrite`: Boolean. Whether to overwrite existing output files
- `skip_errors`: Boolean. Whether to continue processing when a file fails

## Default Configuration

The default configuration is located in `config/default_config.yaml` and looks like this:

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

# Variables to process (if multi-band output needed)
variables: []

# Spatial options
spatial_subset: null

# Processing control
overwrite: false
skip_errors: true
```

## Custom Configuration

To use a custom configuration, create a YAML file with your settings and pass it to the converter:

```bash
nc2cog --config /path/to/my_config.yaml /input/dir /output/dir
```

## Example Custom Configuration

```yaml
# Custom configuration for high-quality compression
compression: "deflate"
zlevel: 9  # Maximum compression
tile_size: [1024, 1024]  # Larger tiles for better performance
block_size: [512, 512]

overviews:
  resampling: "cubic"  # Higher quality resampling
  levels: [2, 4, 8, 16, 32]  # More overview levels

overwrite: true  # Overwrite existing files
skip_errors: true  # Continue if some files fail
```

Note that command-line options override configuration file settings.