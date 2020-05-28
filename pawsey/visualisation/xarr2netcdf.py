import os
import sys
import numpy as np
import xarray as xr
import xgcm
import cartopy.crs as crs
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import seaborn as sns
import cmocean
from pycoawst.tools.circulation import swnmRotate, streamwise_normal, curv2cart, cart2swnm
from pycoawst.tools.grid import sigma2z, metrics
from pycoawst.visualization.plotting import showSlice
from pycoawst.tools.grid import cart2polar

scratch = os.environ['MYSCRATCH']
group = os.environ['MYGROUP']

directory = scratch + "/doneski/"
filepaths = sorted([directory + f + '/results/' for f in os.listdir(directory) ])
additional = sorted([scratch + '/bluewaters/' + f + '/results/' for f in os.listdir(scratch + '/bluewaters/') ])
filepaths.extend(additional)
filepaths

z0 = ['0.0625', '0.25', '001', '004', '016']
lat = ['+00', '-7.5', '-15', '-22.5', '-30']
z0dict = {'016': 4, '004': 3, '001': 2,  '0.25': 1, '0.0625': 0}
latdict = {'+00': 0, '-7.5': 1, '-15': 2,  '-22.5': 3, '-30': 4}

proj = crs.NorthPolarStereo()
omega = 7.29e-5

grdname = group + '/COAWST/Projects/Annulus/smol/ann_grid.nc' 
dg = xr.open_dataset(grdname)
dg['lon_u_polar'], dg['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
dg['lon_v_polar'], dg['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
dg['lon_psi_polar'], dg['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
dg['lon_rho_polar'], dg['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])

vars = ['ubar','vbar','rvorticity_normalized']
info = [{'lon': dg['lon_u_polar'].values, 'lat': dg['lat_u_polar'].values, 'cmax': 0.2},
		  {'lon': dg['lon_v_polar'].values, 'lat': dg['lat_v_polar'].values, 'cmax': 0.2},
		  {'lon': dg['lon_psi_polar'].values, 'lat': dg['lat_psi_polar'].values, 'cmax': 10}]

vardict = dict(zip(vars,info))

#prepare dataframes
dss = {}

for f in filepaths:
	 #identify z0/phi
    latstr = [s for s in lat if s in f.split('/')[5]][0] 
    z0str =  [s for s in z0 if s in f.split('/')[5]][0]
    i = latdict[ latstr ]
    j = z0dict[ z0str ]
    print("lat = " + latstr + "| z0 = " + z0str)  
    avgfiles = [f + ff for ff in sorted(os.listdir(f)) if ff.startswith('ocean_avg_ann')][-2] #fetch average files
    ds = xr.open_mfdataset(avgfiles, decode_times = False, parallel = True, combine='by_coords').mean('ocean_time')
    ds['rvorticity_normalized'] = ds.rvorticity_bar/ds['f'].values.mean()
	 ds['ubar'] *= -1
    dss[i,j] = ds 

