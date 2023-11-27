import os

from scipy import io as sio
import xarray as xr
import numpy as np
from ppgnss import gnss_time
year_from = 2019
year_to = 2020
lat_min, lat_max = -87.5, 87.5
lon_min, lon_max = -180, 180
nequick_dir = "../nequick_matlab/data"
time_list = list()
data_list = list()
for year in range(year_from, year_to):
    for doy in range(1, gnss_time.total_days(year)):
        _, mo, dy = gnss_time.doy2ymd(year, doy)
        for hour in range(0, 24):
            epoch = gnss_time.strtime2datetime("%04d-%02d-%02d %02d:00:00"%(year, mo, dy, hour))
            mat_filename = os.path.join(nequick_dir,
                                        "ne_%04d_%03d_%02d.grid"%(year, doy, hour))
            if not os.path.isfile(mat_filename):
                print("no file %s" % mat_filename)
                continue
            else:
                print(mat_filename)
            data = sio.loadmat(mat_filename)
            data_list.append(data["grid"])
            time_list.append(epoch)

lats = np.arange(lat_min, lat_max+1, 2.5)
lons = np.arange(lon_min, lon_max+1, 5)

xr_data = xr.DataArray(data_list, coords=[time_list, lats, lons],
                       dims=["time", "lat", "lon"])
print(xr_data)
