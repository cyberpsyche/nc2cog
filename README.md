# nc2cog - netCDF to Cloud-Optimized GeoTIFF Converter

Convert netCDF files to Cloud-Optimized GeoTIFF format with advanced compression and performance settings.

## 🚀 Features

- **Format Conversion**: Convert netCDF files to Cloud-Optimized GeoTIFF (COG)
- **Batch Processing**: Process entire directories of netCDF files
- **Advanced Compression**: Support for deflate, lzw, and jpeg compression with configurable levels
- **Performance Optimization**: Configurable tile and block sizes for optimal performance
- **Pyramid Structure**: Customizable overview (pyramid) levels for multi-scale access
- **GDAL Optimized**: Eliminated GDAL warnings and optimized driver-specific parameters
- **Parallel Processing**: Multi-threaded conversion for faster processing
- **Resume Capability**: Resume interrupted conversions

## 📋 Requirements

- Python 3.7+
- GDAL library with Python bindings
- click library for CLI handling
- numpy for numerical operations

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd nc2cog

# Install dependencies
pip install -r requirements.txt

# Install GDAL
# On macOS: brew install gdal
# On Ubuntu: sudo apt-get install gdal-bin libgdal-dev
# On Windows: Use OSGeo4W installer
```

## 🚀 Quick Start

### Basic Usage

Convert a single netCDF file:
```bash
nc2cog input.nc output/
```

Convert all netCDF files in a directory:
```bash
nc2cog input_dir/ output/
```

### Advanced Usage

With custom compression and performance settings:
```bash
nc2cog input.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --tile-size 1024 \
  --block-size 512 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

With parallel processing:
```bash
nc2cog input_dir/ output/ --threads 4
```

## ⚙️ Command Line Options

### Compression Options
- `--compression` [deflate|lzw|jpeg]: Choose compression algorithm
- `--zlevel` [1-9]: Set compression level for deflate (default: 6)

### Performance Options
- `--tile-size` INTEGER: Tile size for COG (default: 512)
- `--block-size` INTEGER: Block size for compression (default: 256)

### Pyramid/Overview Options
- `--resampling` [nearest|bilinear|cubic|...]: Resampling method for overviews (default: nearest)
- `--overview-levels` TEXT: Overview levels (comma-separated, default: 2,4,8,16)

### General Options
- `--overwrite`: Overwrite existing output files
- `--dry-run`: Show what would be processed without doing it
- `--verbose`, `-v`: Enable verbose logging
- `--resume`: Resume from last processed file
- `--threads` INTEGER: Number of parallel processing threads (default: 1)

## 🔧 Configuration File

Create a `config.yaml` for complex setups:

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

## 📊 GDAL Optimization

This tool eliminates common GDAL warnings by using driver-appropriate parameters:

- **GTiff driver**: Uses `BLOCKXSIZE`/`BLOCKYSIZE` instead of `TILEWIDTH`/`TILEHEIGHT`
- **COG driver**: Uses `BLOCKSIZE` instead of `BLOCKXSIZE`/`BLOCKYSIZE`
- **Overview handling**: Optimized to avoid `COPY_SRC_OVERVIEWS` conflicts

## 🎯 Use Cases

### Climate/Meteorological Data
```bash
nc2cog climate_data.nc output/ \
  --compression deflate \
  --zlevel 9 \
  --resampling cubic \
  --overview-levels 2,4,8,16,32
```

### Oceanographic Data
```bash
nc2cog ocean_data.nc output/ \
  --compression lzw \
  --tile-size 1024 \
  --resampling bilinear \
  --overview-levels 2,4,8
```

### Large Dataset Processing
```bash
nc2cog large_dataset/ output/ \
  --threads 4 \
  --compression deflate \
  --zlevel 7 \
  --tile-size 512
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License

## 🐛 Issues

Report issues on the GitHub repository.

## 📚 Documentation

For more detailed documentation:
- [User Guide](docs/user_guide.md)
- [GDAL Optimization Details](docs/gdal_optimization.md)
- [Usage Examples](docs/examples.md)
- [Installation Guide](INSTALLATION.md)
- [Project Structure](docs/project_structure.md)

## ℹ️ Additional Information

### Overview Level Generation

When using `--overview-levels`, note that GDAL intelligently determines which overview levels to actually create based on the source image size. For smaller images, GDAL may generate fewer overview levels than specified to avoid creating overly small and potentially useless overviews.

For example, with `--overview-levels 2,4,8,16,32` on a 1781x1572 image, GDAL may only generate levels 2 and 4 (890x786 and 445x393 pixels respectively) as the smaller levels would be too small to be useful.

---

Made with ❤️ for the geospatial community.