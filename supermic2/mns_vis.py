import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt


gridname = '/work/wtorres/MNS/mns_grid.nc'
gridname = '/work/wtorres/MNS/Results/ocean_his_mns_00003.nc'
H = nc.Dataset(gridname)
lon_rho = G.variables['lon_rho'][:]
print(H)
