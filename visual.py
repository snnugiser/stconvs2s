import os

import numpy as np
import matplotlib.pyplot as plt

from ppgnss import gnss_io
from ppgnss import gnss_utils


outdir = "./output/full-dataset/examples/conv3d"
year_from, year_to = 2018, 2019
rms_new = list()
for i in range(1095):

    pre_filename = os.path.join(outdir, "pre_%04d_%04d_%04d.npy"%(year_from, year_to, i))
    tru_filename = os.path.join(outdir, "tru_%04d_%04d_%04d.npy"%(year_from, year_to, i))

    pre_data = np.load(pre_filename)
    tru_data = np.load(tru_filename)
    for j in range(8):
        delta = pre_data[j,0,0] - tru_data[j,0,0]
        rms = np.sqrt(np.mean(delta*delta))
        rms_new.append(rms)
    # print(i, pre_data.shape, tru_data.shape)

c1pg_dir = "/home/lzhang/TECForecast/data/C1PG"
codg_dir = "/home/lzhang/TECForecast/data/GIM"
c1pg_obj_dir = "/home/lzhang/TECForecast/data/C1PG_OBJ"


obj_copg_filename = "../data/COPG2019_2020.obj"
obj_codg_filename = "../data/CODG2019_2020.obj"
obj_iri_filename = "../data/iri2019_2020.obj"
obj_i20_filename = "../data/i202019_2020.obj"

xr_codg = gnss_utils.loadobject(obj_codg_filename)
xr_copg = gnss_utils.loadobject(obj_copg_filename)
xr_iri = gnss_utils.loadobject(obj_iri_filename)
xr_i20 = gnss_utils.loadobject(obj_i20_filename)

rmss_copg = list()
xr_delta = xr_codg[:,0] - xr_copg[:,0]
for i, time in enumerate(xr_delta.coords["time"].values):
    rms = np.sqrt(np.mean(xr_delta[i].values*xr_delta[i].values))
    rmss_copg.append(rms)

rms_iri = list()
xr_delta_iri = xr_codg[:,0] - xr_iri

rms_i20 = list()
xr_delta_i20 = xr_codg[:,0] - xr_i20

for i, time in enumerate(xr_delta_iri.coords["time"].values):
    rms = np.sqrt(np.mean(xr_delta_iri[i].values*xr_delta_iri[i].values))
    rms_iri.append(rms)

for i, time in enumerate(xr_delta_i20.coords["time"].values):
    rms = np.sqrt(np.mean(xr_delta_i20[i].values*xr_delta_i20[i].values))
    rms_i20.append(rms)

plt.plot(range(len(rms_i20)), rms_iri, label="IRI2020",color='red', 
         linestyle='-', 
         linewidth=1, 
         marker='o', 
         markersize=5,
         mfc="None")

plt.plot(range(len(rms_iri)), rms_iri, label="IRI2016",color='yellow', 
         linestyle='-', 
         linewidth=1, 
         marker='o', 
         markersize=5,
         mfc="None")

plt.plot(range(len(rmss_copg)), rmss_copg, label="COPG",color='green', 
         linestyle='-', 
         linewidth=1, 
         marker='o', 
         markersize=5,
         mfc="None")


plt.plot(range(len(rms_new)), rms_new, label="EML",color='blue', 
         linestyle='-', 
         linewidth=1, 
         marker='o', 
         markersize=5,
         mfc="None")


xticks = range(0, len(rms_iri), 6*4)
xticklables = ["%d" %(_//(6)) for _ in xticks]
# plt.xticks(xticks, xticklables)
# plt.ylim((0, 1.5))
plt.legend()
plt.ylabel("RMS (TECU)")
plt.xlabel("Time (Hour)")

# plt.plot(rms_iri, "y.")
plt.show()