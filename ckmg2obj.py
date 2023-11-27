import os
import datetime

import numpy as np
import xarray as xr

from ppgnss import gnss_io
from ppgnss import gnss_time
from ppgnss import gnss_utils
from ppgnss import gnss_geodesy

import utils
import geo2mag

key = "CKMG"
ckmg_dir = "/Users/lzhang/research/TEC_forcast/data/CKMG"
out_dir = "../data"
ckmg_dir = "../data/%s"%key

time_list = list()
data_list = list()

year_from, doy_from = 2017, 1
year_to, doy_to = 2018, 1

outfilename = os.path.join(out_dir, "%s%04d_%04d.obj" %(key, year_from, year_to))

jd_from = gnss_time.doy2jd(year_from, doy_from)
jd_to = gnss_time.doy2jd(year_to, doy_to)
ndays = int(jd_to - jd_from)
dataset = np.zeros((ndays*24, 71, 73))
iday = 0
nepoch_in_day = 24
if os.path.isfile(outfilename):
    xr_data = gnss_utils.loadobject(outfilename)
else:
    for year in range(year_from, year_to):
        days_in_year = gnss_time.total_days(year)
        for doy in range(1, days_in_year+1):
            _, mon, dy = gnss_time.doy2ymd(year, doy)
            fn = os.path.join(ckmg_dir, "%s%03d0.%02dI" %(key, doy, year-2000))
            print(fn)
            xr_ckmg = gnss_io.read_ionex_file(fn)
            dataset[iday*24:(iday+1)*24] = xr_ckmg.values[:24, :]
            iday += 1
            time_list.extend(xr_ckmg.coords["time"].values[:24])
    xr_data = xr.DataArray(dataset, coords={"time": time_list,
                                "lat": xr_ckmg.coords["lat"].values,
                                "lon": xr_ckmg.coords["lon"]})

    gnss_utils.saveobject(xr_data, outfilename)
    print(outfilename + " is saved!")
print(xr_data)

import matplotlib.pyplot as plt
# print(xr_iri.coords["lon"].values)

plt.imshow(xr_data[0].values)
plt.show()


