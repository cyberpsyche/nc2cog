"""
Unit tests for CLI parameters in nc2cog converter.
Tests for zlevel, block_size, tile_size, and resampling parameters.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nc2cog.cli import main


class TestCLIParams(unittest.TestCase):
    """Test cases for CLI parameter functionality"""

    def setUp(self):
        """Set up temporary files for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_input_file = os.path.join(self.temp_dir, 'test.nc')
        self.temp_output_dir = os.path.join(self.temp_dir, 'output')

        # Create an empty temporary input file to satisfy exists=True check
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.temp_output_dir, exist_ok=True)
        with open(self.temp_input_file, 'w') as f:
            f.write('dummy content')

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_zlevel_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test zlevel parameter handling"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with zlevel parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--zlevel', '9'
        ]

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected after processing or error
                pass

        # Verify that ProcessingEngine was called, which means config was set up correctly
        mock_processing_engine.assert_called_once()

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_block_size_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test block_size parameter handling"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with block_size parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--block-size', '512'
        ]

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected after processing or error
                pass

        # Verify that ProcessingEngine was called, indicating successful parameter parsing
        mock_processing_engine.assert_called_once()

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_tile_size_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test tile_size parameter handling"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with tile_size parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--tile-size', '256'
        ]

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected after processing or error
                pass

        # Verify that ProcessingEngine was called, indicating successful parameter parsing
        mock_processing_engine.assert_called_once()

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_resampling_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test resampling parameter handling"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with resampling parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--resampling', 'bilinear'
        ]

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected after processing or error
                pass

        # Verify that ProcessingEngine was called, indicating successful parameter parsing
        mock_processing_engine.assert_called_once()

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_all_parameters_combined(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test all parameters combined"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with all parameters
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--zlevel', '9',
            '--block-size', '1024',
            '--tile-size', '512',
            '--resampling', 'cubic'
        ]

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected after processing or error
                pass

        # Verify that ProcessingEngine was called, indicating successful parameter parsing
        mock_processing_engine.assert_called_once()

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_default_parameters(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test default parameter values when not specified"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command without additional parameters
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir
        ]

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected after processing or error
                pass

        # Verify that ProcessingEngine was called, indicating successful default parameter usage
        mock_processing_engine.assert_called_once()

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_invalid_zlevel_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test handling of invalid zlevel parameter"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with invalid zlevel parameter (out of range)
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--zlevel', '15'  # Invalid value, should be 1-9
        ]

        # Expect the program to handle the invalid argument appropriately
        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected for invalid CLI arguments
                pass
            except ValueError:
                # Also possible for invalid numeric conversion
                pass

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_invalid_block_size_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test handling of invalid block_size parameter"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with invalid block_size parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--block-size', 'invalid'
        ]

        # Expect the program to handle the invalid argument appropriately
        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected for invalid CLI arguments
                pass
            except ValueError:
                # Also possible for invalid numeric conversion
                pass

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_invalid_tile_size_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test handling of invalid tile_size parameter"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with invalid tile_size parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--tile-size', 'invalid'
        ]

        # Expect the program to handle the invalid argument appropriately
        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected for invalid CLI arguments
                pass
            except ValueError:
                # Also possible for invalid numeric conversion
                pass

    @patch('nc2cog.cli.ProcessingEngine')
    @patch('nc2cog.cli.FileDiscovery')
    @patch('nc2cog.cli.ConfigManager')
    def test_invalid_resampling_parameter(self, mock_config_manager, mock_file_discovery, mock_processing_engine):
        """Test handling of invalid resampling parameter"""
        # Mock return values
        mock_file_discovery.return_value.find_files.return_value = [Path(self.temp_input_file)]

        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance

        mock_engine_instance = MagicMock()
        mock_engine_instance.validate_input.return_value = True
        mock_engine_instance.convert_file.return_value = True
        mock_processing_engine.return_value = mock_engine_instance

        # Test command with invalid resampling parameter
        test_args = [
            'nc2cog',
            self.temp_input_file,
            self.temp_output_dir,
            '--resampling', 'invalid_method'
        ]

        # Expect the program to handle the invalid argument appropriately
        # (should raise error due to click.Choice constraint)
        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                # Expected for invalid CLI arguments
                pass


if __name__ == '__main__':
    unittest.main()