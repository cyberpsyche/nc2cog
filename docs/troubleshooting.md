# Troubleshooting Guide for netCDF to COG TIFF Converter

## Common Issues

### Installation Issues

**Problem**: Installation fails with GDAL-related errors
**Solution**: Install GDAL separately first. The converter requires GDAL with Python bindings. On Ubuntu:
```bash
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)
```

On macOS with Homebrew:
```bash
brew install gdal
pip install GDAL==$(gdal-config --version)
```

### File Format Issues

**Problem**: Converter says "Cannot open file as netCDF"
**Solution**: Verify that the file is actually a netCDF file and that GDAL can read it. Try opening it with:
```bash
gdalinfo /path/to/file.nc
```

**Problem**: "No raster bands found in netCDF"
**Solution**: The netCDF file may not contain geospatial raster data in a format GDAL recognizes. Check the file structure with tools like `ncdump -h`.

### Memory Issues

**Problem**: Process runs out of memory on large files
**Solution**: The converter processes one file at a time, but large files may require significant memory. Ensure your system has enough RAM for the largest file you're processing.

### Disk Space Issues

**Problem**: Process fails partway through
**Solution**: The converter creates temporary files during processing. Ensure you have sufficient disk space in your output directory (temporary files may be similar in size to the input file).

## Error Messages

### "Failed to open netCDF file"
- Cause: File is corrupted, not a netCDF file, or inaccessible
- Solution: Verify the file exists and is a valid netCDF file

### "Output path does not exist"
- Cause: Output directory doesn't exist
- Solution: Create the output directory before running the converter

### "Invalid configuration" errors
- Cause: Configuration file contains invalid values
- Solution: Check the configuration against the configuration guide

## Performance Tips

### Optimizing Speed
- Use JPEG compression for imagery data (faster compression/decompression)
- Increase tile size for better performance with large files
- Process files in parallel using the `--threads` option

### Optimizing Quality
- Use Deflate compression for scientific data
- Use Cubic resampling for overviews to preserve quality
- Adjust zlevel for Deflate compression (higher values = better compression but slower)

## Getting Help

If you encounter an issue not covered here:

1. Enable verbose logging with `--verbose` to get more detailed error information
2. Check that your GDAL installation is working correctly
3. Verify that the netCDF files can be read by GDAL
4. Share the error message and your configuration when seeking help