import os.path
from os import path

import numpy as np

from ppgnss import gnss_utils

    
year_from, year_to = 2020, 2021

obj_filename_train = path.join("../data", "CODG%04d_%04d.obj" %(year_from, year_to))
obj_filename_test = path.join("../data", "CODG%04d_%04d.obj" %(year_from+1, year_to+1))

xr_dataset_train = gnss_utils.loadobject(obj_filename_train)

xr_dataset_test = gnss_utils.loadobject(obj_filename_test)

indexes = np.arange(xr_dataset_train.values.shape[0])
np.random.shuffle(indexes) # 打乱
train_index = indexes[: int(0.9 * len(indexes))]
val_index = indexes[int(0.9 * len(indexes)) :]
x_train = xr_dataset_train[train_index, 1:].values
y_train = xr_dataset_train[train_index, 0:1].values

x_val = xr_dataset_train[val_index, 1:].values
y_val = xr_dataset_train[val_index, 0:1].values

x_test = xr_dataset_test[:, 1:].values
y_test = xr_dataset_test[:, 0:1].values

x_train_path = "data/x_train_%04d_%04d.obj" %(year_from, year_to)
y_train_path = "data/y_train_%04d_%04d.obj" %(year_from, year_to)
x_val_path = "data/x_val_%04d_%04d.obj" %(year_from, year_to)
y_val_path = "data/y_val_%04d_%04d.obj" %(year_from, year_to)
x_test_path = "data/x_test_%04d_%04d.obj" %(year_from, year_to)
y_test_path = "data/y_test_%04d_%04d.obj" %(year_from, year_to)

gnss_utils.saveobject(x_train, x_train_path)
gnss_utils.saveobject(y_train, y_train_path)
gnss_utils.saveobject(x_val, x_val_path)
gnss_utils.saveobject(y_val, y_val_path)
gnss_utils.saveobject(x_test, x_test_path)
gnss_utils.saveobject(y_test, y_test_path)