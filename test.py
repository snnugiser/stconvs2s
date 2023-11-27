import os

import numpy as np
import matplotlib.pyplot as plt

from ppgnss import gnss_io
from ppgnss import gnss_utils


obj_copg_filename = "../data/COPG2019_2020.obj"
obj_codg_filename = "../data/CODG2019_2020.obj"
obj_iri_filename = "../data/iri2019_2020.obj"
obj_i20_filename = "../data/i202019_2020.obj"

# xr_codg = gnss_utils.loadobject(obj_codg_filename)
# xr_copg = gnss_utils.loadobject(obj_copg_filename)
xr_iri = gnss_utils.loadobject(obj_iri_filename)
# xr_i20 = gnss_utils.loadobject(obj_i20_filename)


# print(xr_iri)
# xarray python 
# print(xr_iri.loc["2019-01-01 00:00:00",-87.5, -180])
# print(xr_iri[0,0,0])

import matplotlib.pyplot as plt
# print(xr_iri.coords["lon"].values)

plt.imshow(xr_iri[0].values)
plt.show()

#  一、生成2016-2022 IRI
# 1. run_iri.py
# 2. run sh
# 3. run iri2obj.py

# 二、