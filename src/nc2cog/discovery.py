"""File discovery service for netCDF to COG TIFF converter."""

import os
import fnmatch
from pathlib import Path
from typing import List, Iterator, Optional
from .errors import FileDiscoveryError


class FileDiscovery:
    """Discovers and manages netCDF files for conversion."""

    def __init__(self, input_path: Path, pattern: str = "*.nc"):
        """
        Initialize file discovery service.

        Args:
            input_path: Input directory or file path
            pattern: File pattern to match (default: "*.nc")
        """
        self.input_path = input_path
        self.pattern = pattern

    def find_files(self) -> List[Path]:
        """
        Find all matching netCDF files in the input path.

        Returns:
            List of Path objects pointing to netCDF files

        Raises:
            FileDiscoveryError: If input path doesn't exist or is invalid
        """
        if not self.input_path.exists():
            raise FileDiscoveryError(f"Input path does not exist: {self.input_path}")

        if self.input_path.is_file():
            # Single file input
            if self._matches_pattern(self.input_path.name):
                return [self.input_path]
            else:
                raise FileDiscoveryError(f"Input file does not match pattern {self.pattern}: {self.input_path}")

        # Directory input - scan recursively
        netcdf_files = []
        for root, dirs, files in os.walk(self.input_path):
            for file in fnmatch.filter(files, self.pattern):
                netcdf_files.append(Path(root) / file)

        return sorted(netcdf_files)

    def _matches_pattern(self, filename: str) -> bool:
        """
        Check if filename matches the pattern.

        Args:
            filename: Name of the file to check

        Returns:
            True if the file matches the pattern
        """
        return fnmatch.fnmatch(filename, self.pattern)

    def find_files_generator(self) -> Iterator[Path]:
        """
        Generator that yields netCDF files one by one (memory efficient).

        Yields:
            Path objects pointing to netCDF files
        """
        if not self.input_path.exists():
            raise FileDiscoveryError(f"Input path does not exist: {self.input_path}")

        if self.input_path.is_file():
            # Single file input
            if self._matches_pattern(self.input_path.name):
                yield self.input_path
            else:
                raise FileDiscoveryError(f"Input file does not match pattern {self.pattern}: {self.input_path}")
        else:
            # Directory input - scan recursively
            for root, dirs, files in os.walk(self.input_path):
                for file in fnmatch.filter(files, self.pattern):
                    yield Path(root) / file

    def get_resume_state(self, output_dir: Path, input_files: List[Path]) -> List[Path]:
        """
        Get list of files that still need to be processed based on resume state.

        Args:
            output_dir: Output directory where converted files would be placed
            input_files: List of all input files to process

        Returns:
            List of files that still need to be processed
        """
        if not output_dir.exists():
            return input_files

        remaining_files = []
        for input_file in input_files:
            # Generate expected output path
            relative_path = input_file.relative_to(self.input_path)
            output_path = output_dir / relative_path.with_suffix('.tif')

            if not output_path.exists():
                remaining_files.append(input_file)

        return remaining_files