"""Custom exceptions for netCDF to COG TIFF converter."""

class NC2COGError(Exception):
    """Base exception for nc2cog tool."""
    pass


class FileDiscoveryError(NC2COGError):
    """Raised when file discovery fails."""
    pass


class ConversionError(NC2COGError):
    """Raised when conversion fails."""
    pass


class ConfigError(NC2COGError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(NC2COGError):
    """Raised when validation fails."""
    pass