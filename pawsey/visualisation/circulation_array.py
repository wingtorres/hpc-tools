import os
import sys
import numpy as np
import xarray as xr
import cartopy.crs as crs
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import seaborn as sns
import cmocean

from pycoawst.tools.grid import cart2polar

scratch = os.environ['MYSCRATCH']
group = os.environ['MYGROUP']

filepaths = sorted([f for f in os.listdir(group + "/COAWST/hpc-tools/pawsey/visualisation/") if f.startswith("smol")])

z0 = ['0.0625', '0.25', '001', '004', '016']
lat = ['+00', '-7.5', '-15', '-22.5', '-30']
z0dict = {'016': 4, '004': 3, '001': 2,  '0.25': 1, '0.0625': 0}
latdict = {'+00': 0, '-7.5': 1, '-15': 2,  '-22.5': 3, '-30': 4}

proj = crs.NorthPolarStereo()
plt.rcParams["text.usetex"] = False

grdname = group + '/COAWST/Projects/Annulus/smol/ann_grid.nc' 
dg = xr.open_dataset(grdname)
dg['lon_u_polar'], dg['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
dg['lon_v_polar'], dg['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
dg['lon_psi_polar'], dg['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
dg['lon_rho_polar'], dg['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])

def axisfix(axis, lon, lat, var, cmax = None):
	with sns.axes_style("white", rc={'text.usetex':False}):
		
		axis.set_extent([80,100,89.825,89.9125], crs=crs.PlateCarree())

		pc = axis.pcolormesh(lon, lat, var, transform = crs.PlateCarree(),
					  cmap = cmocean.cm.balance, vmin = -cmax, vmax = cmax, #norm = norm, 
					  edgecolor = [0,0,0.25], linewidth = 0, rasterized = True)
		
		axis.outline_patch.set_visible(False)
		axis.spines['left'].set_visible(True)  
		axis.spines['bottom'].set_visible(True)  
		axis.spines['right'].set_visible(True) 
		axis.spines['top'].set_visible(True) 
		axis.outline_patch.alpha = .25
		axis.outline_patch.color = 'gray'
	
	return pc

vars = ['ubar','vbar','zeta','rvorticity_bar']
info = [{'lon': dg['lon_u_polar'].values, 'lat': dg['lat_u_polar'].values, 'cmax': 0.2},
		  {'lon': dg['lon_v_polar'].values, 'lat': dg['lat_v_polar'].values, 'cmax': 0.2}, 
		  {'lon': dg['lon_rho_polar'].values, 'lat': dg['lat_rho_polar'].values, 'cmax': 0.0025},
		  {'lon': dg['lon_psi_polar'].values, 'lat': dg['lat_psi_polar'].values, 'cmax': 1e-3}]

vardict = dict(zip(vars,info))

#prepare dataframes
dss = {}

for f in filepaths:

	#identify z0/phi
    latstr = [s for s in lat if s in f.split('/')[-1]][0] 
    z0str =  [s for s in z0 if s in f.split('/')[-1]][0]
    i = latdict[ latstr ]
    j = z0dict[ z0str ]
    #print("lat = " + latstr + " // z0 = " + z0str)  
    dss[i,j] = xr.open_dataset( "{}/avgplus.nc".format(f), decode_times = False) 

for key,var in vardict.items():

	print('plotting {}...'.format(key))
	
	fig, axes = plt.subplots(nrows = len(z0), ncols = len(lat), squeeze = False, figsize = (5.5,3.9), sharex = True, sharey = True, subplot_kw=dict(projection=proj))

	for (i,j),ds in dss.items():
		
		axis = axes[i,j]		
		pc = axisfix(axis = axis, lon = var['lon'] + 90, lat = var['lat'], var = np.squeeze(ds[key]), cmax = var['cmax'])
		
		#labeling
		if axis.is_first_row():
			axis.set_title( '{} cm'.format( ds['Zob'].values*100) , fontsize = 8)
		if axis.is_first_col():
			axis.text(-0.125,0.5, '{0:.1f}'.format( 180*np.arcsin(ds['f'].values.mean()/(2*7.29e-5))/np.pi ) + '$^{\circ}$S', fontsize = 8, 
			horizontalalignment = 'right', verticalalignment = 'center', transform = axis.transAxes)
		
	shrink = 1
	cb = fig.colorbar(pc, ax = axes[-1,:], location = "bottom", anchor = (0.5, 0), shrink = shrink, aspect = 60, fraction = 0.2, pad = .25)
	cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
	cb.outline.set_linewidth(0.25)
	#cb.ax.set_title("{}".format(key), fontsize = 8) 

	fig.subplots_adjust(wspace = 0, hspace = 0)
	plt.savefig("{}.png".format(key), dpi = 1200, bbox_inches = "tight")
