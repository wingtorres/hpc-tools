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

filepaths = sorted([f for f in os.listdir(group + "/hpc-tools/pawsey/visualisation/") if f.startswith("smol")])
proj = crs.NorthPolarStereo()
plt.rcParams["text.usetex"] = False

grdname = group + '/COAWST/Projects/Annulus/smol/ann_grid.nc' 
dg = xr.open_dataset(grdname)
dg['lon_u_polar'], dg['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
dg['lon_v_polar'], dg['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
dg['lon_psi_polar'], dg['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
dg['lon_rho_polar'], dg['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])

def axisfix(axis, lon, lat, var, cmax = None, cmap = cmocean.cm.balance, norm = False ):
	
	if not norm:
		norm = colors.Normalize(vmin=-cmax,vmax=cmax)
	
	with sns.axes_style("white", rc={'text.usetex':False}):
		
		#axis.set_extent([80,100,89.825,89.9125], crs=crs.PlateCarree())
		axis.set_extent([77.5,102.5,89.825,89.9125], crs=crs.PlateCarree())
		
		pc = axis.pcolormesh(lon.values + 90, lat.values, np.squeeze(var.values), transform = crs.PlateCarree(),
					  cmap = cmap, vmin = -cmax, vmax = cmax, norm = norm, 
					  edgecolor = [0,0,0.25], linewidth = 0, rasterized = True)
		
		axis.outline_patch.set_visible(False)
		axis.spines['left'].set_visible(True)  
		axis.spines['bottom'].set_visible(True)  
		axis.spines['right'].set_visible(True) 
		axis.spines['top'].set_visible(True) 
		axis.outline_patch.alpha = .25
		axis.outline_patch.color = 'gray'
	
	return pc


#surface circulation field plot
def circvis(ds, filename = "circ", sigma = -1):
		  
		  fig, ax = plt.subplots(nrows = 1, ncols = 3, squeeze = False, figsize = (5.5,3.9), sharex = True, sharey = True, subplot_kw=dict(projection=proj))
		  
		  pu = axisfix(ax[0,0], dg['lon_u_polar'], dg['lat_u_polar'], ds['u'].isel(s_rho = sigma), cmax = 0.25)
		  pv = axisfix(ax[0,1], dg['lon_v_polar'], dg['lat_v_polar'], ds['v'].isel(s_rho = sigma), cmax = 0.25)
		  #pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['rvorticity'].isel(s_rho = sigma)/ds['f'].mean(), cmax = 1e1, cmap = cmocean.cm.curl)
		  pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['alpha'].isel(s_rho = sigma), cmax = np.pi, cmap = mpl.cm.twilight_shifted)
		  
		  ax[0,0].text(0.9, 0.05, "$u$", transform=ax[0,0].transAxes, size=8)
		  ax[0,1].text(0.9, 0.05, "$v$", transform=ax[0,1].transAxes, size=8)
		  ax[0,2].text(0.9, 0.05, r"$ \alpha $", transform=ax[0,2].transAxes, size=8)
		  
		  cb = fig.colorbar(pu, ax = ax[0], location = "bottom", anchor = (0, -.05), shrink = 2/3, aspect = 60, fraction = 0.2, pad = .25)
		  cb.ax.set_xlabel("Velocity (m/s)", fontsize = 8)
		  cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
		  cb.outline.set_linewidth(0.25) 
		   
		  cb = fig.colorbar(pw, ax = ax[0], location = "bottom", anchor = (1, -4.875), shrink = 1/3, aspect = 30, fraction = 0.2, pad = .25)
		  cb.ax.set_xlabel("Direction (rads)", fontsize = 8)
		  cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
		  cb.outline.set_linewidth(0.25) 
		  
		  fig.subplots_adjust(wspace = 0, hspace = 0) 
		  fig.suptitle( "$\sigma = {}$".format(sigma), y = 0.5) 
		  plt.savefig("{}.png".format(filename), dpi = 1200, bbox_inches = "tight")

def momvis(ds, filename = "mom", sigma = -1):
	
	norm=colors.SymLogNorm(linthresh=1e-7, linscale=0.1, vmin=-1e-4, vmax=1e-4, base=10)	
	
	momentum_terms = ['accel','cor','hadv','fsco','hjvf','hvisc','kvrf','prsgrd','vadv','vjvf','vvisc','wbrk'] 

	fig, ax = plt.subplots(nrows = 4, ncols = 3, squeeze = True, figsize = (5.5,5.0), sharex = True, sharey = True, subplot_kw=dict(projection=proj))
	
	for k,m in enumerate(momentum_terms):
		axis = ax.flatten()[k]
		pm = axisfix(axis, dg['lon_u_polar'], dg['lat_u_polar'], ds[m].isel(s_rho = sigma), cmax = 1e-4, norm = norm)
		axis.text(0.75, 0.1, "{}".format(m), transform=axis.transAxes, size=6)
	
	cb = fig.colorbar(pm, ax = ax[-1,:], location = "bottom", anchor = (0.5, 0), shrink = 1.0, aspect = 60, fraction = 0.2, pad = .25)
	cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
	cb.outline.set_linewidth(0.25)	
	
	fig.subplots_adjust(wspace = 0, hspace = 0)
	plt.savefig("{}.png".format(filename), dpi = 1200, bbox_inches = "tight")

#for f in filepaths[:1]:
f = filepaths[-4]
print(f)
cirname = f + '/avgplus.nc'
swname = f + '/sw.nc'
nmname = f + '/nm.nc'

dc = xr.open_dataset(cirname, decode_times = False)
sw = xr.open_dataset(swname, decode_times = False) 
nm = xr.open_dataset(nmname, decode_times = False)
circvis(dc, filename = "circ_surf", sigma = -1)
circvis(dc, filename = "circ_bott", sigma = 0)
momvis(sw, filename = "sw_surf", sigma = -1)
momvis(sw, filename = "sw_bott", sigma = 0)
momvis(nm, filename = "nm_surf", sigma = -1)
momvis(nm, filename = "nm_bott", sigma = 0)
