# Usage Example

## Sample Usage of netCDF to COG TIFF Converter

This example demonstrates how to use the tool in practice. 

### 1. Basic Usage

```bash
# Convert all netCDF files in a directory to COG TIFF files
nc2cog /path/to/netcdf/files /path/to/output/cog/files
```

### 2. With Configuration File

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

### 3. Advanced Options

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

### 4. Sample Configuration for Different Use Cases

#### For Scientific Data (High Compression)
```yaml
compression: "deflate"
zlevel: 9
tile_size: [512, 512]
block_size: [256, 256]
overviews:
  resampling: "cubic"
  levels: [2, 4, 8, 16, 32]
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
overwrite: false
skip_errors: true
```

### 5. Processing Large Datasets

For processing large datasets, consider:

- Using `--threads` to process multiple files in parallel
- Choosing appropriate tile sizes for your data access patterns
- Enabling resume capability to recover from interruptions
- Using `--dry-run` first to estimate processing time and disk space needs

### 6. Error Handling

The tool includes robust error handling:

- Individual file failures don't stop the entire batch process
- Errors are logged with detailed information
- Resume functionality allows recovery from interruptions
- Validation ensures input files are properly formatted

This makes it suitable for production environments where reliability is essential.