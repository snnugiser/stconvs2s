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

key = "GIM"
#key = "c1p"
key = "COPG"

gim_dir = "/Users/lzhang/research/TEC_forcast/data/GIM"
# gim_dir = "../data/GIM"
out_dir = "../data"
gim_dir = "../data/%s"%key

time_list = list()
data_list = list()
year_from, doy_from = 2016, 1
year_to, doy_to = 2017, 1
outfilename = os.path.join(out_dir, "%s%04d_%04d.obj" %(key, year_from, year_to))



jd_from = gnss_time.doy2jd(year_from, doy_from)
jd_to = gnss_time.doy2jd(year_to, doy_to)
ndays = int(jd_to - jd_from)
dataset = np.zeros((ndays*24, 13, 71, 73))
iday = 0
nepoch_in_day = 24
for year in range(year_from, year_to):
    days_in_year = gnss_time.total_days(year)
    for doy in range(1, days_in_year+1):
        _, mon, dy = gnss_time.doy2ymd(year, doy)
        fn = os.path.join(gim_dir, "%s%03d0.%02dI" %(key, doy, year-2000))
        print(fn)
        xr_gim = gnss_io.read_ionex_file(fn)
        dataset[iday*24:(iday+1)*24, 0] = xr_gim.values[:24, :, :]

        solar_dec = utils.solar_declination(doy, unit="radius")
        solar_dec_deg = np.rad2deg(solar_dec)

        coord_time = xr_gim.coords["time"].values
        delta_hours = (coord_time - np.datetime64(datetime.datetime(year=year, month=mon, day=int(dy)))) / np.timedelta64(1,
                                                                                                                     "h")
        hours_volumn, lat_volumn, lon_volumn = np.meshgrid(delta_hours, xr_gim.coords["lat"].values, xr_gim.coords["lon"].values, indexing="ij")

        local_time_volumn = lon_volumn*24/360 + hours_volumn #  地方时, hour

        h_volumn = np.deg2rad(15*(local_time_volumn-12))  # 时角, radius
        solar_altitude_sine = np.cos(h_volumn)*np.cos(solar_dec)*np.cos(np.deg2rad(lat_volumn)) + np.sin(solar_dec)*np.sin(np.deg2rad(lat_volumn))
        noon_solar_altitude_sine = np.cos(solar_dec)*np.cos(np.deg2rad(lat_volumn)) + np.sin(solar_dec)*np.sin(np.deg2rad(lat_volumn))
        solar_altitude_radius = np.arcsin(solar_altitude_sine)
        solar_altitude = gnss_geodesy.radian2degree(solar_altitude_radius )
        noon_solar_altitude_radius = np.arcsin(noon_solar_altitude_sine)
        # noon_solar_altitude = gnss_geodesy.radian2degree(noon_solar_altitude_radius )

        solar_azimuth_cos =(np.sin(solar_dec)*np.cos(np.deg2rad(lat_volumn)) - np.cos(h_volumn)*np.cos(solar_dec)*np.sin(np.deg2rad(lat_volumn)))/np.cos(np.arcsin(solar_altitude_sine))
        solar_azimuth_cos[solar_azimuth_cos>1]=1
        solar_azimuth_cos[solar_azimuth_cos<-1]=-1
        solar_azimuth_radius = np.arccos(solar_azimuth_cos)
        solar_azimuth_radius[h_volumn>0] = np.pi-solar_azimuth_radius[h_volumn>0]

        # solar_azimuth_radius[solar_altitude_radius<0] = 0
        solar_altitude_radius[solar_altitude_radius<0] = 0

        omega_cos = -np.tan(np.deg2rad(lat_volumn)) * np.tan(solar_dec)

        sunset_time = np.abs(np.arccos(omega_cos)*12/np.pi) + 12   # 日落时间，与时角有12小时的差异。
        sunrise_time = 24 - sunset_time

        hours_from_sunset = local_time_volumn - sunset_time
        hours_from_sunset[solar_altitude>0] = 0
        hours_from_sunset[hours_from_sunset<0] += 24

        polar_day_or_night = np.zeros(hours_from_sunset.shape)
        if solar_dec > 0:
            polar_day_or_night[lat_volumn>90-solar_dec_deg] = -1 # polar day
            polar_day_or_night[lat_volumn<-90+solar_dec_deg] = 1 # polar night
        else:
            polar_day_or_night[lat_volumn<-90-solar_dec_deg] = -1
            polar_day_or_night[lat_volumn>90+solar_dec_deg] = 1

        hours_from_sunset[polar_day_or_night==1] = 24

        lat_grid, lon_grid = np.meshgrid(xr_gim.coords["lat"].values, xr_gim.coords["lon"].values, indexing="ij")
        mag_lat, mag_lon = geo2mag.geo2mag(lat_grid, lon_grid)
        mag_lat_rad = np.deg2rad(mag_lat)
        mag_lon_rad = np.deg2rad(mag_lon)
        mag_lat_grid = np.repeat(mag_lat_rad.reshape(1, 71, 73), nepoch_in_day, axis=0)
        mag_lon_grid = np.repeat(mag_lon_rad.reshape(1, 71, 73), nepoch_in_day, axis=0)

        dataset[iday*24:(iday+1)*24, 1] = np.sin(solar_altitude_radius[:24])
        dataset[iday*24:(iday+1)*24, 2] = np.cos(solar_altitude_radius[:24])
        dataset[iday*24:(iday+1)*24, 3] = np.sin(solar_azimuth_radius[:24])
        dataset[iday*24:(iday+1)*24, 4] = np.cos(solar_azimuth_radius[:24])
        dataset[iday*24:(iday+1)*24, 5] = np.sin(noon_solar_altitude_radius[:24])
        dataset[iday*24:(iday+1)*24, 6] = np.cos(noon_solar_altitude_radius[:24])
        dataset[iday*24:(iday+1)*24, 7] = hours_from_sunset[:24]
        dataset[iday*24:(iday+1)*24, 8] = polar_day_or_night[:24]
        dataset[iday*24:(iday+1)*24, 9] = np.sin(mag_lat_grid[:24])
        dataset[iday*24:(iday+1)*24, 10] = np.cos(mag_lat_grid[:24])
        dataset[iday*24:(iday+1)*24, 11] = np.sin(mag_lon_grid[:24])
        dataset[iday*24:(iday+1)*24, 12] = np.cos(mag_lon_grid[:24])

        iday += 1
        time_list.extend(xr_gim.coords["time"].values[:24])
xr_data = xr.DataArray(dataset, coords={"time": time_list,
                                        "band": ["tec", "sin_solar_altitude", "cos_solar_altitude",
                                                 "sin_solar_azimuth", "cos_azimuth",
                                                 "sin_noon_solar_altitude", "cos_noon_solar_altitude",
                                                 "hours_from_sunset", "polar_day_or_night",
                                                 "sin_mag_lat", "cos_mag_lon",
                                                 "sin_mag_lon", "cos_mag_lon"],
                                        "lat": xr_gim.coords["lat"].values,
                                        "lon": xr_gim.coords["lon"]})

gnss_utils.saveobject(xr_data, outfilename)
print(outfilename + " is saved!")