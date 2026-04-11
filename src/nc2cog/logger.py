"""Logging service for netCDF to COG TIFF converter."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    verbose: bool = False,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up and configure the logger for the application.

    Args:
        verbose: Enable verbose logging if True
        log_file: Optional path to log file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('nc2cog')

    # Clear existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set level
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger