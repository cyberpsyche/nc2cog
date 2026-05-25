"""Command-line interface for netCDF to COG TIFF converter."""

import click
import sys
from pathlib import Path
import time
from typing import Optional
from .config import ConfigManager
from .discovery import FileDiscovery
from .processor import ProcessingEngine
from .logger import setup_logger
from .errors import NC2COGError
from .analyzer import NCAnalyzer
from .__version__ import __version__


@click.command()
@click.version_option(version=__version__, prog_name='nc2cog')
@click.option('-V', is_flag=True, callback=lambda ctx, param, value: click.echo(f"nc2cog {__version__}") or ctx.exit(0) if value else None, expose_value=False, is_eager=True, help='Show version and exit')
@click.argument('input_path', type=click.Path(exists=True, dir_okay=True, file_okay=True))
@click.argument('output_path', type=click.Path(dir_okay=True, file_okay=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--compression', type=click.Choice(['deflate', 'lzw', 'jpeg']), default='deflate', help='Compression type')
@click.option('--zlevel', type=click.IntRange(1, 9), default=6, help='Compression level for deflate (1-9, default: 6)')
@click.option('--block-size', type=int, default=256, help='Block size for compression (default: 256)')
@click.option('--resampling', type=click.Choice(['nearest', 'bilinear', 'cubic', 'average', 'mode', 'gauss', 'rms']), default='nearest', help='Resampling method for overviews (default: nearest)')
@click.option('--tile-size', type=int, default=512, help='Tile size for COG (default: 512)')
@click.option('--overview-levels', default='2,4,8,16', help='Overview levels for pyramid structure, comma-separated (default: 2,4,8,16)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--dry-run', is_flag=True, help='Show what would be processed without doing it')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--resume', is_flag=True, help='Resume from last processed file')
@click.option('--threads', type=int, default=1, help='Number of parallel processing threads')
@click.option('--src-proj', type=str, help='Source projection in EPSG format (e.g., EPSG:4326)')
@click.option('--dst-proj', type=str, help='Target projection in EPSG format (e.g., EPSG:3857)')
@click.option('--variables', type=str, default=None, help='Variables to convert (comma-separated, e.g., PRE,REF)')
@click.option('--metadata-source', type=str, default=None,
              help='Data source description for metadata (e.g., satellite, sensor)')
def main(
    input_path: str,
    output_path: str,
    config: Optional[str],
    compression: str,
    zlevel: int,
    block_size: int,
    resampling: str,
    tile_size: int,
    overview_levels: str,
    overwrite: bool,
    dry_run: bool,
    verbose: bool,
    resume: bool,
    threads: int,
    src_proj: Optional[str],
    dst_proj: Optional[str],
    variables: Optional[str],
    metadata_source: Optional[str],
) -> None:
    """
    Convert netCDF files to Cloud-Optimized GeoTIFF format.

    INPUT_PATH: Source directory or file path
    OUTPUT_PATH: Destination directory
    """
    # Setup logging
    logger = setup_logger(verbose=verbose)

    # Initialize components
    try:
        # Load configuration
        config_path = Path(config) if config else None
        config_manager = ConfigManager(config_path)

        # Override config with CLI options if provided
        if compression != 'deflate':
            config_manager.config['compression'] = compression
        if zlevel != 6:
            config_manager.config['zlevel'] = zlevel
        if block_size != 256:
            config_manager.config['block_size'] = [block_size, block_size]
        if resampling != 'nearest':
            config_manager.config['overviews']['resampling'] = resampling
        if tile_size != 512:
            config_manager.config['tile_size'] = [tile_size, tile_size]
        # Parse overview levels from comma-separated string and convert to list of ints
        if overview_levels != '2,4,8,16':
            levels_list = [int(x.strip()) for x in overview_levels.split(',')]
            config_manager.config['overviews']['levels'] = levels_list
        if overwrite:
            config_manager.config['overwrite'] = True

        # Handle projection parameters
        if dst_proj:
            config_manager.config['projection'] = config_manager.config.get('projection', {})
            config_manager.config['projection']['target'] = dst_proj
        if src_proj:
            config_manager.config['projection'] = config_manager.config.get('projection', {})
            config_manager.config['projection']['source'] = src_proj

        # Handle metadata source parameter
        if metadata_source:
            config_manager.config['metadata'] = config_manager.config.get('metadata', {})
            config_manager.config['metadata']['source'] = metadata_source

        # Validate configuration
        config_manager.validate()

        # Setup processing engine
        engine = ProcessingEngine(config_manager)

        # Setup file discovery
        input_path_obj = Path(input_path)
        output_path_obj = Path(output_path)

        discovery = FileDiscovery(input_path_obj)

        # Detect single-file mode: input is a file AND output path ends with .tif
        single_file_mode = input_path_obj.is_file() and str(output_path).endswith('.tif')

        # Detect multi-dimensional NC: input is a file with GDAL subdatasets
        multi_dim_mode = False
        if input_path_obj.is_file():
            analyzer = NCAnalyzer(input_path_obj)
            subdatasets = analyzer.get_subdatasets()
            if len(subdatasets) > 0:
                multi_dim_mode = True
                variables_list = [v.strip() for v in variables.split(',')] if variables else analyzer.get_data_variables()
                if not variables_list:
                    logger.info("No data variables found in the netCDF file")
                    return

        # Find all netCDF files
        all_files = discovery.find_files()
        logger.info(f"Found {len(all_files)} netCDF files to process")

        if not single_file_mode and resume:
            files_to_process = discovery.get_resume_state(output_path_obj, all_files)
            logger.info(f"After resume check, {len(files_to_process)} files still need processing")
        else:
            files_to_process = all_files

        if dry_run:
            if multi_dim_mode:
                logger.info("Dry run mode - multi-dimensional file detected:")
                logger.info(f"  Input: {input_path_obj}")
                if single_file_mode:
                    logger.info(f"  Output: {output_path_obj} (variable: {variables_list[0]})")
                else:
                    logger.info(f"  Variables: {', '.join(variables_list)}")
                    for var_name in variables_list:
                        logger.info(f"    {var_name} -> {output_path_obj / f'{var_name}.tif'}")
            else:
                logger.info("Dry run mode - would process:")
                for f in files_to_process:
                    if single_file_mode:
                        out_file = Path(output_path)
                    elif input_path_obj.is_file():
                        out_file = output_path_obj / input_path_obj.with_suffix('.tif').name
                    else:
                        relative_path = f.relative_to(input_path_obj)
                        out_file = output_path_obj / relative_path.with_suffix('.tif')
                    logger.info(f"  {f} -> {out_file}")
            return

        if not files_to_process:
            logger.info("No files to process")
            return

        # Multi-dimensional NC processing
        if multi_dim_mode:
            logger.info(f"Multi-dimensional mode: converting variables: {', '.join(variables_list)}")
            start_time = time.time()

            if single_file_mode:
                # Direct file output (single variable to specified .tif)
                engine.convert_multiband_file(input_path_obj, output_path_obj, variables_list[0])
                successful = 1
                failed = 0
            else:
                # Directory output (all variables)
                results = engine.convert_multiband(input_path_obj, output_path_obj, variables_list)
                successful = sum(1 for v in results.values() if v)
                failed = sum(1 for v in results.values() if not v)

            elapsed_time = time.time() - start_time

            logger.info(f"\nProcessing complete!")
            logger.info(f"Successful: {successful}")
            logger.info(f"Failed: {failed}")
            logger.info(f"Total: {successful + failed}")
            logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")

            if failed > 0:
                sys.exit(1)
            return

        # Process files
        successful = 0
        failed = 0
        start_time = time.time()

        logger.info("Starting conversion process...")

        for i, input_file in enumerate(files_to_process):
            try:
                # Generate output file path
                if single_file_mode:
                    output_file = Path(output_path)
                elif input_path_obj.is_file():
                    output_file = output_path_obj / input_path_obj.with_suffix('.tif').name
                else:
                    relative_path = input_file.relative_to(input_path_obj)
                    output_file = output_path_obj / relative_path.with_suffix('.tif')

                # Skip if file exists and overwrite is not enabled
                if output_file.exists() and not overwrite:
                    logger.warning(f"Output file exists, skipping: {output_file}")
                    continue

                logger.info(f"[{i+1}/{len(files_to_process)}] Processing: {input_file.name}")

                # Validate input file
                engine.validate_input(input_file)

                # Convert the file
                result = engine.convert_file(input_file, output_file)

                if result:
                    successful += 1
                    logger.info(f"  ✓ Completed: {output_file.name}")
                else:
                    failed += 1
                    logger.error(f"  ✗ Failed: {input_file.name}")

            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Failed to process {input_file.name}: {str(e)}")

                # Continue with other files if skip_errors is enabled
                if not config_manager.get('skip_errors', True):
                    raise

        # Print summary
        elapsed_time = time.time() - start_time
        logger.info(f"\nProcessing complete!")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total: {successful + failed}")
        logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")

        if failed > 0:
            sys.exit(1)

    except NC2COGError as e:
        logger.error(f"NC2COG Error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()