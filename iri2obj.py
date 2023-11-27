import os

import numpy as np
import xarray as xr
from ppgnss import gnss_io
from ppgnss import gnss_utils
from ppgnss import gnss_time

dir_name = "/Volumes/Research/genera_program/IRI_2016_proj/out"
dir_name = "/home/lzhang/TECForecast/IRI_2016_proj/out"
dir_name = "/home/lzhang/TECForecast/IRI-2020/out"

time_list = list()
data_list = list()
year_from = 2017
year_to = 2018
iri_obj_filename = "../data/i20%04d_%04d.obj" %(year_from, year_to)
if not os.path.isfile(iri_obj_filename):
    for year in range(year_from, year_to):
        ndays = gnss_time.total_days(year)
        for doy in range(1, ndays+1):
            for hour in range(0, 24):
                filename = "IRI_%04d_%03d_%02d.TAB" %(year, doy, hour)
                fullname = os.path.join(dir_name, filename)
                print(fullname)
                xr_iri_hr = gnss_io.read_iri_web(fullname)
                # print(xr_iri_hr)
                time_list.append(xr_iri_hr.coords["time"].values[0])
                data_list.append(xr_iri_hr[0].values)
    xr_iri = xr.DataArray(data_list, coords=[time_list, xr_iri_hr.coords["lat"].values, xr_iri_hr.coords["lon"].values],
                          dims=["time", "lat", "lon"])
    gnss_utils.saveobject(xr_iri, iri_obj_filename)
else:
    xr_iri = gnss_utils.loadobject(iri_obj_filename)
    print("file %s is exist" % iri_obj_filename)

import matplotlib.pyplot as plt
# print(xr_iri.coords["lon"].values)

plt.imshow(xr_iri[0].values)
plt.show()

# print(xr_iri)
