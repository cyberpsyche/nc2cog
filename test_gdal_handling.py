#!/usr/bin/env python3
"""Test script to verify GDAL import handling in the processor."""

import sys
from unittest.mock import patch
from pathlib import Path

# Test the import when GDAL is available
print("Testing with GDAL available...")
try:
    from src.nc2cog.processor import ProcessingEngine, GDAL_AVAILABLE
    print(f"GDAL_AVAILABLE: {GDAL_AVAILABLE}")

    if GDAL_AVAILABLE:
        print("✓ GDAL import succeeded when available")
    else:
        print("? GDAL not available on this system (this is OK)")

    # Test accessing processor functionality
    from src.nc2cog.config import ConfigManager
    config = ConfigManager()
    engine = ProcessingEngine(config)
    print("✓ ProcessingEngine instantiated successfully")

except Exception as e:
    print(f"✗ Error during normal operation: {e}")


# Mock GDAL not being available
print("\nTesting GDAL import handling with mocked unavailability...")
with patch('src.nc2cog.processor.GDAL_AVAILABLE', False), \
     patch('src.nc2cog.processor.gdal', None), \
     patch('src.nc2cog.processor.osr', None):

    # Reload the module to simulate GDAL not being available
    import importlib
    import src.nc2cog.processor
    importlib.reload(src.nc2cog.processor)

    from src.nc2cog.processor import GDAL_AVAILABLE, ProcessingEngine
    print(f"After mocking unavailability - GDAL_AVAILABLE: {GDAL_AVAILABLE}")

    from src.nc2cog.config import ConfigManager
    config = ConfigManager()
    engine = ProcessingEngine(config)

    # Test that methods properly handle GDAL unavailability
    try:
        engine.calculate_memory_usage(Path("dummy.nc"))
        print("✓ calculate_memory_usage handled missing GDAL gracefully")
    except Exception as e:
        if "GDAL is not available" in str(e):
            print("✓ calculate_memory_usage properly raised GDAL error as expected")
        else:
            print(f"? Unexpected error from calculate_memory_usage: {e}")

print("\n✓ GDAL handling verification complete")