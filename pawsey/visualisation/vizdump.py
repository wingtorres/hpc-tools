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
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#import matplotlib.font_manager
#plt.rcParams["font.serif"] = "Computer Modern Roman"
plt.rcParams["text.usetex"] = False

def axisfix(axis, lon, lat, var, cmax = None):
	with sns.axes_style("white", rc={'text.usetex':False}):
		
		axis.set_extent([80,100,89.825,89.9125], crs=crs.PlateCarree())

		#norm = colors.TwoSlopeNorm(vmin = var.min(), vcenter=0, vmax = var.max())
		pc = axis.pcolormesh(lon, lat, var, transform = crs.PlateCarree(),
					  cmap = cmocean.cm.balance, vmin = -cmax, vmax = cmax, #norm = norm, 
					  edgecolor = [0,0,0.25], linewidth = 0, rasterized = True)
		
		#gl = axis.gridlines(linewidth = 0.15,  alpha = 0.5, color = 'gray')
		#gl.n_steps = 360
		axis.outline_patch.set_visible(False)
		#axis.axes.get_xaxis().set_visible(False)
		#axis.axes.get_yaxis().set_visible(False)
		axis.spines['left'].set_visible(True)  
		axis.spines['bottom'].set_visible(True)  
		axis.spines['right'].set_visible(True) 
		axis.spines['top'].set_visible(True) 
		axis.outline_patch.alpha = .25
		axis.outline_patch.color = 'gray'

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

for key,var in vardict.items():
	print('plotting {}...'.format(key))

	fig, axes = plt.subplots(nrows = len(z0), ncols = len(lat), squeeze = False, figsize = (5.5,3.9), sharex = True, sharey = True, subplot_kw=dict(projection=proj))

	for (i,j),ds in dss.items():
		
		axis = axes[i,j]		
		axisfix(axis = axis, lon = var['lon'] + 90, lat = var['lat'], var = ds[key], cmax = var['cmax'])
		
		#labeling
		if axis.is_first_row():
			axis.set_title( '{} cm'.format( ds['Zob'].values*100) , fontsize = 8)
		if axis.is_first_col():
			axis.text(-0.125,0.5, '{0:.1f}'.format( 180*np.arcsin(ds['f'].values.mean()/(2*omega))/np.pi ) + '$^{\circ}$S', fontsize = 8, 
			horizontalalignment = 'right', verticalalignment = 'center', transform = axis.transAxes)

		fig.subplots_adjust(wspace = 0, hspace = 0)
		plt.savefig("{}.png".format(key), bbox_inches = "tight")


