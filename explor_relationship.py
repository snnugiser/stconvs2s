import os
from scipy import io as sio
import numpy as np
import matplotlib.pyplot as plt

from ppgnss import gnss_utils

obj_codg_filename = "../data/CODG2019_2020.obj"


xr_codg = gnss_utils.loadobject(obj_codg_filename)

fig, axes = plt.subplots(nrows=1, ncols=7)

axes[0].scatter(np.arcsin(xr_codg[0,1].values),
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)



axes[1].scatter(np.arcsin(xr_codg[0,3].values),
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)


axes[2].scatter(np.arcsin(xr_codg[0,5].values),
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)

axes[3].scatter(xr_codg[0,7].values,
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)

axes[4].scatter(xr_codg[0,8].values,
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)

axes[5].scatter(np.arcsin(xr_codg[0,9].values),
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)
axes[6].scatter(np.arcsin(xr_codg[0,11].values),
            xr_codg[0,0].values, 
            c=xr_codg[0,0].values)

plt.show()