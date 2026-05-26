"""Version information for netCDF to COG TIFF converter."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nc2cog")
except PackageNotFoundError:
    __version__ = "unknown"
