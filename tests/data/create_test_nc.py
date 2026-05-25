"""Create a small test netCDF file for metadata tests."""
import numpy as np
import netCDF4
from pathlib import Path

DATA_DIR = Path(__file__).parent
OUTPUT = DATA_DIR / "sample.nc"

def create_sample_nc():
    nc = netCDF4.Dataset(str(OUTPUT), 'w', format='NETCDF4')
    nc.source = "Test Satellite"
    nc.institution = "Test Lab"

    # Dimensions
    nc.createDimension('lat', 10)
    nc.createDimension('lon', 10)
    nc.createDimension('time', 3)

    # Coordinate variables
    lat = nc.createVariable('lat', 'f4', ('lat',))
    lat[:] = np.linspace(-5, 5, 10)
    lat.units = "degrees_north"

    lon = nc.createVariable('lon', 'f4', ('lon',))
    lon[:] = np.linspace(100, 110, 10)
    lon.units = "degrees_east"

    time = nc.createVariable('time', 'f8', ('time',))
    time[:] = [0, 1, 2]
    time.units = "days since 2025-01-01"

    # Data variable
    data = nc.createVariable('temperature', 'f4', ('time', 'lat', 'lon'))
    data.units = "K"
    data[:] = np.random.rand(3, 10, 10) * 100 + 200

    nc.close()
    print(f"Created {OUTPUT}")

if __name__ == '__main__':
    create_sample_nc()
