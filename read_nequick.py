import os
from scipy import io as sio
import numpy as np
import matplotlib.pyplot as plt

from ppgnss import gnss_utils

eml_dir = "./output/full-dataset/examples/conv3d"
i=0
pre_filename = os.path.join(eml_dir, "pre_%04d.npy"%i)
tru_filename = os.path.join(eml_dir, "tru_%04d.npy"%i)
pre_data = np.load(pre_filename)
tru_data = np.load(tru_filename)
# print(.shape)
obj_copg_filename = "../data/COPG2019_2020.obj"
obj_codg_filename = "../data/eml2019_2020.obj"
obj_iri_filename = "../data/iri2019_2020.obj"
obj_i20_filename = "../data/i202019_2020.obj"

xr_codg = gnss_utils.loadobject(obj_codg_filename)
# xr_copg = gnss_utils.loadobject(obj_copg_filename)
# xr_iri = gnss_utils.loadobject(obj_iri_filename)
# xr_i20 = gnss_utils.loadobject(obj_i20_filename)

data = sio.loadmat("/home/lzhang/TECForecast/nequick_matlab/data/ne_2019_001_00.grid")
# print(xr_codg[0,0].values.shape)
delta = xr_codg[0,0].values - data["grid"]
# print(np.sqrt(np.mean(delta*delta)))

vmin = 0
vmax = 50
fig, axes = plt.subplots(2,4)
im = axes[0][0].imshow(pre_data[0,0,0], vmin=vmin, vmax=vmax, cmap="jet")
plt.colorbar(im, ax=axes[0][0])

im = axes[0][1].imshow(tru_data[0,0,0], vmin=vmin, vmax=vmax, cmap="jet")
plt.colorbar(im, ax=axes[0][1])

im = axes[0][2].imshow(data["grid"], vmin=vmin, vmax=vmax, cmap="jet")
plt.colorbar(im, ax=axes[0][2])

im = axes[0][3].imshow(xr_codg[0,0].values, vmin=vmin, vmax=vmax, cmap="jet")
plt.colorbar(im, ax=axes[0][3])

vmin, vmax = -10, 10
im = axes[1][0].imshow(pre_data[0,0,0]-xr_codg[0,0].values, vmin=vmin, vmax=vmax, cmap="jet")
plt.colorbar(im, ax=axes[1][0])

im = axes[1][2].imshow(data["grid"]-xr_codg[0,0].values, vmin=vmin, vmax=vmax, cmap="jet")
plt.colorbar(im, ax=axes[1][2])

plt.show()
