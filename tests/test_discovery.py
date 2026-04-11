"""Tests for file discovery service."""

import pytest
from pathlib import Path
import tempfile
from src.nc2cog.discovery import FileDiscovery, FileDiscoveryError


def test_single_file_discovery():
    """Test discovery of a single netCDF file."""
    with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as f:
        temp_file = Path(f.name)

    try:
        discovery = FileDiscovery(temp_file)
        files = discovery.find_files()
        assert len(files) == 1
        assert files[0] == temp_file
    finally:
        temp_file.unlink()


def test_single_non_matching_file():
    """Test error when single file doesn't match pattern."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        temp_file = Path(f.name)

    try:
        discovery = FileDiscovery(temp_file)
        with pytest.raises(FileDiscoveryError):
            discovery.find_files()
    finally:
        temp_file.unlink()


def test_directory_discovery():
    """Test discovery of netCDF files in directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some netCDF files
        nc_files = []
        for i in range(3):
            nc_file = temp_path / f"file{i}.nc"
            nc_file.touch()
            nc_files.append(nc_file)

        # Create some non-netCDF files
        (temp_path / "file.txt").touch()
        (temp_path / "file.jpg").touch()

        discovery = FileDiscovery(temp_path)
        files = discovery.find_files()

        assert len(files) == 3
        for nc_file in nc_files:
            assert nc_file in files


def test_recursive_directory_discovery():
    """Test discovery of netCDF files in subdirectories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create subdirectory
        subdir = temp_path / "subdir"
        subdir.mkdir()

        # Create netCDF files in main and sub directory
        main_nc = temp_path / "main.nc"
        main_nc.touch()

        sub_nc = subdir / "sub.nc"
        sub_nc.touch()

        # Create non-matching files
        (temp_path / "main.txt").touch()
        (subdir / "sub.txt").touch()

        discovery = FileDiscovery(temp_path)
        files = discovery.find_files()

        assert len(files) == 2
        assert main_nc in files
        assert sub_nc in files


def test_custom_pattern():
    """Test discovery with custom file pattern."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create files with different extensions
        (temp_path / "data.nc").touch()
        (temp_path / "data.nc4").touch()  # netCDF-4
        (temp_path / "data.txt").touch()

        # Discover with custom pattern
        discovery = FileDiscovery(temp_path, pattern="*.nc4")
        files = discovery.find_files()

        assert len(files) == 1
        assert files[0].name == "data.nc4"


def test_nonexistent_path():
    """Test error when path doesn't exist."""
    nonexistent_path = Path("/nonexistent/path")
    discovery = FileDiscovery(nonexistent_path)

    with pytest.raises(FileDiscoveryError):
        discovery.find_files()


def test_empty_directory():
    """Test discovery in empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        discovery = FileDiscovery(temp_path)
        files = discovery.find_files()

        assert len(files) == 0


def test_get_resume_state():
    """Test resume state calculation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create input directory structure
        input_dir = temp_path / "input"
        input_dir.mkdir()

        # Create output directory structure
        output_dir = temp_path / "output"
        output_dir.mkdir()

        # Create some input files
        input_files = []
        for i in range(3):
            inp_file = input_dir / f"file{i}.nc"
            inp_file.touch()
            input_files.append(inp_file)

        # Create output files for some inputs (simulating partial completion)
        completed_output = output_dir / "file0.tif"
        completed_output.touch()

        discovery = FileDiscovery(input_dir)
        remaining = discovery.get_resume_state(output_dir, input_files)

        # Should only return files that don't have corresponding outputs
        assert len(remaining) == 2
        expected_remaining = [input_dir / "file1.nc", input_dir / "file2.nc"]
        for exp_file in expected_remaining:
            assert exp_file in remaining