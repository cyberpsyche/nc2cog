# Usage Example

## Sample Usage of netCDF to COG TIFF Converter

This example demonstrates how to use the tool in practice. 

### 1. Basic Usage

```bash
# Convert all netCDF files in a directory to COG TIFF files
nc2cog /path/to/netcdf/files /path/to/output/cog/files
```

### 2. Introduction

This example demonstrates how to use the tool in practice.

### 3. With Configuration File

First, create a configuration file (`config.yaml`):

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

Then use it with the tool:

```bash
nc2cog --config config.yaml /path/to/input /path/to/output
```

### 4. GDAL Warnings Reduction

The tool now includes optimizations to reduce GDAL warnings during processing:

```bash
# Reduced GDAL warnings for cleaner output
nc2cog --quiet /path/to/input /path/to/output

# Or use verbose mode for detailed processing info without warnings
nc2cog -v /path/to/input /path/to/output
```

**Note:** The updated parameter handling reduces unnecessary GDAL warnings while preserving important processing information.

### 5. Parameter Optimizations

The tool now includes improved parameter handling with enhanced GDAL compatibility:

```bash
# Improved parameter validation and GDAL optimization
nc2cog --compression jpeg --tile-size 1024 --optimization gdal /path/to/input /path/to/output

# Process with reduced GDAL warnings and higher compression
nc2cog --compression deflate --zlevel 9 --quiet /path/to/input /path/to/output

# Use optimized block size for better GDAL performance
nc2cog --block-size 512 --gdal-optimize /path/to/input /path/to/output

# Use custom tile size with GDAL-specific optimizations
nc2cog --tile-size 1024 --gdal-cache 1024 /path/to/input /path/to/output

# Enhanced resampling with GDAL parameter tuning
nc2cog --resampling cubic --gdal-tiff-params /path/to/input /path/to/output

# Resume interrupted processing with optimized GDAL settings
nc2cog --resume --gdal-optimize /path/to/input /path/to/output

# Verbose logging with filtered GDAL messages
nc2cog -v --threads 4 --gdal-verbose /path/to/input /path/to/output

# Dry run with parameter validation
nc2cog --dry-run --validate-params /path/to/input /path/to/output

# Combining multiple optimized parameters
nc2cog --compression deflate --zlevel 8 --tile-size 1024 --block-size 512 --resampling cubic --gdal-optimize /path/to/input /path/to/output
```

### 6. Advanced Options

```bash
# Process with JPEG compression for imagery data
nc2cog --compression jpeg --tile-size 1024 /path/to/input /path/to/output

# Process with higher compression level
nc2cog --compression deflate --zlevel 9 /path/to/input /path/to/output

# Use custom block size for compression
nc2cog --block-size 512 /path/to/input /path/to/output

# Use custom tile size for better performance
nc2cog --tile-size 1024 /path/to/input /path/to/output

# Use cubic resampling for high-quality overviews
nc2cog --resampling cubic /path/to/input /path/to/output

# Resume interrupted processing
nc2cog --resume /path/to/input /path/to/output

# Verbose logging to monitor progress
nc2cog -v --threads 4 /path/to/input /path/to/output

# Dry run to see what would be processed
nc2cog --dry-run /path/to/input /path/to/output

# Combining multiple parameters
nc2cog --compression deflate --zlevel 8 --tile-size 1024 --block-size 512 --resampling cubic /path/to/input /path/to/output
```

### 7. Sample Configuration for Different Use Cases

#### For Scientific Data (High Compression)
```yaml
compression: "deflate"
zlevel: 9
tile_size: [512, 512]
block_size: [256, 256]
overviews:
  resampling: "cubic"
  levels: [2, 4, 8, 16, 32]
gdal_options:
  optimize_gdal_warnings: true
  cache_size_mb: 1024
  tiling_scheme: "COG"
overwrite: false
skip_errors: true
```

#### For Imagery Data (Fast Access)
```yaml
compression: "jpeg"
tile_size: [1024, 1024]
block_size: [512, 512]
overviews:
  resampling: "average"
  levels: [2, 4, 8, 16]
gdal_options:
  optimize_gdal_warnings: true
  cache_size_mb: 512
  tiling_scheme: "COG"
overwrite: false
skip_errors: true
```

### 8. Processing Large Datasets

For processing large datasets, consider:

- Using `--threads` to process multiple files in parallel
- Choosing appropriate tile sizes for your data access patterns
- Enabling resume capability to recover from interruptions
- Using `--dry-run` first to estimate processing time and disk space needs
- Leveraging GDAL optimizations to reduce warnings and improve performance with `--gdal-optimize`
- Adjusting GDAL cache size with `--gdal-cache` for better memory management during large conversions

### 9. Error Handling

The tool includes robust error handling:

- Individual file failures don't stop the entire batch process
- Errors are logged with detailed information
- Resume functionality allows recovery from interruptions
- Validation ensures input files are properly formatted

This makes it suitable for production environments where reliability is essential.

### 10. GDAL Warning Reduction and Parameter Handling Improvements

The updated tool includes several improvements to reduce GDAL warnings and enhance parameter handling:

- **Reduced verbosity**: Unnecessary GDAL warnings are now suppressed while maintaining important information
- **Parameter validation**: Enhanced validation prevents invalid parameter combinations
- **Optimized defaults**: Default GDAL settings are now tuned for netCDF to COG conversion
- **Memory management**: Improved cache handling prevents memory overflow during large conversions
- **Configurable options**: New `--quiet` and `--gdal-verbose` flags allow control over GDAL output
- **Configuration options**: The `gdal_options` section in configuration files allows fine-tuning of GDAL parameters