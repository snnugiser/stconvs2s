import requests
import time
import os
import numpy as np
from ppgnss import gnss_time
from ppgnss import gnss_utils

url = "https://nequick-g.jrc.ec.europa.eu/nequick.php"
outdir = "../data/nequick_gim"
gal_ai_file = "Galieo_IONO.2019"
year = 2019
nrows = 71
ncols = 73
lat_min = -87.5
lat_max = 87.5
lon_min = -180.
lon_max = 180.
lat_step, lon_step = 2.5, 5.
gal_ais = np.loadtxt(gal_ai_file, dtype={"names":["doy", "a0", "a1", "a2"],
                                        "formats":["int", "float", "float", "float"]})
doy_from = 1
for idoy, (doy, a0, a1, a2) in enumerate( zip(gal_ais["doy"][doy_from-1:], 
                                              gal_ais["a0"][doy_from-1:], 
                                              gal_ais["a1"][doy_from-1:], 
                                              gal_ais["a2"][doy_from-1:])):
    print(year, doy)
    _, mo, dy = gnss_time.doy2ymd(year, int(doy))
    for ut in range(0, 24):
        for ilat, lat in enumerate( np.arange(lat_min, lat_max+1, lat_step)[0:]):
            irow = int((lat - lat_min)/lat_step)
            outfile = os.path.join(outdir, "NeQuick_%04d_%03d_%02d_%02d.obj" % (year, doy, ut,irow))
            data = np.zeros(ncols)
            for ilon, lon in enumerate( np.arange(lon_min, lon_max, lon_step)):
                data = {
                    "a0": a0, #2.7500E1,
                    "a1": a1, #4.6875E-02,
                    "a2": a2, #4.3640E-03,
                    "month": mo,
                    "utc": ut,

                    "lb1": lon,
                    "ph1": lat,
                    "h1":0,

                    "lb2":lon,
                    "ph2": lat,
                    "h2": 20107681.66
                }

                respose = requests.post(url, data=data)
                result=respose.text
                idx0 = result.find("Nequick estimates")
                idx1 = result.find("TECU")

                tec = float(result[idx0+17:idx1])
                data[ilon] = tec
                time.sleep(4)
                print(lat, lon, tec)
            print(outfile + " is saved!")
            gnss_utils.saveobject(data, outfile)