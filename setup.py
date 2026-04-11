from setuptools import setup, find_packages

setup(
    name="nc2cog",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "GDAL>=3.8.0",
        "click>=8.1.0",
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "nc2cog=nc2cog.cli:main",
        ],
    },
    author="Your Name",
    description="Tool for converting netCDF files to Cloud-Optimized GeoTIFF format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)