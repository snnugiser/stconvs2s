from os import path
import datetime

import numpy as np

import geo2mag
from ppgnss import gnss_io
from ppgnss import gnss_time
from ppgnss import gnss_geodesy
from ppgnss import gnss_utils

import utils

def main():
    # gim_dir = "/Users/lzhang/research/TEC_forcast/data/GIM"
    gim_dir = "../data/GIM"

    test_year_from, test_doy_from = 2012, 1
    test_year_to, test_doy_to = 2022, 315
    jd_from = gnss_time.doy2jd(test_year_from, test_doy_from)
    jd_to = gnss_time.doy2jd(test_year_to, test_doy_to)
    window_size = 50 # days
    windos_start_days = np.arange(jd_from, jd_to, window_size)
    trainning_days_delta = range(0, 30, 1)
    validation_days_delta = range(30, 40, 1)
    testing_days_delta = range(40, 50, 1)

    nwindows = len(windos_start_days)
    nrows = 71
    ncols = 73

    nbands = 13
    nepoch_in_day = 12
    input_len = 1 # days
    output_len = 1 # days
    data_set = np.ndarray(shape=(nwindows, window_size, nbands, input_len*nepoch_in_day, nrows, ncols))
    data_set_y = np.ndarray(shape=(nwindows, window_size, nbands, output_len*nepoch_in_day, nrows, ncols))
    for ind_windw, window_start_day in enumerate(windos_start_days):
        # test_jd = gnss_time.doy2jd(test_year, test_doy)
        days_in_window = [tmp + window_start_day for tmp in range(window_size)]

        band_TEC = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols)) # VTEC
        band_solar_altitude = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols)) # solar altitude
        band_solar_azimuth = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols)) # solar azimuth
        band_solar_noon_solar_altitude = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols)) # Noon solar altitude angle
        band_hours_from_sunset = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols)) # hours from sunset
        band_polar_day_or_night = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols)) # polar day or night
        band_mag_lat = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols))
        band_mag_lon = np.ndarray(shape=(window_size, nepoch_in_day, nrows, ncols))
        # for year, mon, dy in sample_set:
        for ind_in_window, jd_trainning_day in enumerate(days_in_window):
            year, mon, dy = gnss_time.jd2ymd(jd_trainning_day)
            year1, doy = gnss_time.ymd2doy(year, mon, dy)
            print(ind_windw, ind_in_window, year, mon, dy)

            # print(year, mon, dy, doy)

            gim_filename = path.join(gim_dir, "CODG%03d0.%02dI" %(doy, year-2000))
            # gim_filename = "/Users/lzhang/research/TEC_forcast/data/GIM/CODG3480.22I"
            print(gim_filename)
            xr_gim = gnss_io.read_ionex_file(gim_filename)
            if len(xr_gim.coords["time"].values)==25:
                xr_gim = xr_gim.loc[::2, :, :]
            xr_gim = xr_gim[:12]  # 第13张图与第二天重复，只取前12张图
            band_TEC[ind_in_window] = xr_gim.values
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

            band_solar_altitude[ind_in_window] = solar_altitude_radius
            band_solar_azimuth[ind_in_window] = solar_azimuth_radius
            band_solar_noon_solar_altitude[ind_in_window] = noon_solar_altitude_radius
            band_hours_from_sunset[ind_in_window] = hours_from_sunset
            band_polar_day_or_night[ind_in_window] = polar_day_or_night
            band_mag_lat[ind_in_window] = mag_lat_grid
            band_mag_lon[ind_in_window] = mag_lon_grid

        data_set[ind_windw, :, 0] = band_TEC
        # data_set[ind_windw, :, 1] = band_solar_altitude
        # data_set[ind_windw, :, 2] = band_solar_azimuth
        # data_set[ind_windw, :, 3] = band_solar_noon_solar_altitude
        # data_set[ind_windw, :, 4] = band_hours_from_sunset
        # data_set[ind_windw, :, 5] = band_polar_day_or_night

        data_set[ind_windw, :, 1] = np.sin(band_solar_altitude)
        data_set[ind_windw, :, 2] = np.cos(band_solar_altitude)
        data_set[ind_windw, :, 3] = np.sin(band_solar_azimuth)
        data_set[ind_windw, :, 4] = np.cos(band_solar_azimuth)
        data_set[ind_windw, :, 5] = np.sin(band_solar_noon_solar_altitude)
        data_set[ind_windw, :, 6] = np.cos(band_solar_noon_solar_altitude)
        data_set[ind_windw, :, 7] = band_hours_from_sunset
        data_set[ind_windw, :, 8] = band_polar_day_or_night
        data_set[ind_windw, :, 9] = np.sin(band_mag_lat)
        data_set[ind_windw, :, 10] = np.cos(band_mag_lat)
        data_set[ind_windw, :, 11] = np.sin(band_mag_lon)
        data_set[ind_windw, :, 12] = np.cos(band_mag_lon)

    obj_filename = path.join("../data", "band13_windows80_windowsize50_epochs12.obj")
    # obj_filename = path.join("../data/dataset", "windows80_windowsize50_epochs12_factor_model.obj")
    print("saving %s" % obj_filename)
    gnss_utils.saveobject(data_set, obj_filename)
    print(obj_filename+ " is saved!")


if __name__ == "__main__":
    main()