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


@click.command()
@click.argument('input_path', type=click.Path(exists=True, dir_okay=True, file_okay=True))
@click.argument('output_path', type=click.Path(dir_okay=True, file_okay=False))
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--compression', type=click.Choice(['deflate', 'lzw', 'jpeg']), default='deflate', help='Compression type')
@click.option('--zlevel', type=click.IntRange(1, 9), default=6, help='Compression level for deflate (1-9, default: 6)')
@click.option('--block-size', type=int, default=256, help='Block size for compression (default: 256)')
@click.option('--resampling', type=click.Choice(['nearest', 'bilinear', 'cubic', 'average', 'mode', 'gauss', 'rms']), default='nearest', help='Resampling method for overviews (default: nearest)')
@click.option('--tile-size', type=int, default=512, help='Tile size for COG (default: 512)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing output files')
@click.option('--dry-run', is_flag=True, help='Show what would be processed without doing it')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--resume', is_flag=True, help='Resume from last processed file')
@click.option('--threads', type=int, default=1, help='Number of parallel processing threads')
def main(
    input_path: str,
    output_path: str,
    config: Optional[str],
    compression: str,
    zlevel: int,
    block_size: int,
    resampling: str,
    tile_size: int,
    overwrite: bool,
    dry_run: bool,
    verbose: bool,
    resume: bool,
    threads: int
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
        if overwrite:
            config_manager.config['overwrite'] = True

        # Validate configuration
        config_manager.validate()

        # Setup processing engine
        engine = ProcessingEngine(config_manager)

        # Setup file discovery
        input_path_obj = Path(input_path)
        output_path_obj = Path(output_path)

        discovery = FileDiscovery(input_path_obj)

        # Find all netCDF files
        all_files = discovery.find_files()
        logger.info(f"Found {len(all_files)} netCDF files to process")

        if resume:
            files_to_process = discovery.get_resume_state(output_path_obj, all_files)
            logger.info(f"After resume check, {len(files_to_process)} files still need processing")
        else:
            files_to_process = all_files

        if dry_run:
            logger.info("Dry run mode - would process:")
            for f in files_to_process:
                relative_path = f.relative_to(input_path_obj)
                output_file = output_path_obj / relative_path.with_suffix('.tif')
                logger.info(f"  {f} -> {output_file}")
            return

        if not files_to_process:
            logger.info("No files to process")
            return

        # Process files
        successful = 0
        failed = 0
        start_time = time.time()

        logger.info("Starting conversion process...")

        for i, input_file in enumerate(files_to_process):
            try:
                # Generate output file path
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