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

from pycoawst.tools.grid import cart2polar, metrics

scratch = os.environ['MYSCRATCH']
group = os.environ['MYGROUP']

filepaths = sorted(["runs/{}".format(f) for f in os.listdir(group + "/hpc-tools/pawsey/visualisation/runs/") if f.startswith("smol")])
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
							 cmap = cmap, shading = "nearest", norm = norm, edgecolor = [0,0,0.25], linewidth = 0, rasterized = True)

		#axis.outline_patch.set_visible(False)
		axis.spines['left'].set_visible(True)  
		axis.spines['bottom'].set_visible(True)  
		axis.spines['right'].set_visible(True) 
		axis.spines['top'].set_visible(True) 
		#axis.outline_patch.alpha = .25
		#axis.outline_patch.color = 'gray'

	return pc


#surface circulation field plot
def circvis(ds, filename = "circ", sigma = None, cmax = None, flux = False):

	fig, ax = plt.subplots(nrows = 1, ncols = 3, squeeze = False, figsize = (5.5,3.9), sharex = True, sharey = True, subplot_kw=dict(projection=proj))

	if sigma and not flux:  
		pu = axisfix(ax[0,0], dg['lon_u_polar'], dg['lat_u_polar'], ds['u_radial'].isel(s_rho = sigma), cmax = cmax)
		pv = axisfix(ax[0,1], dg['lon_v_polar'], dg['lat_v_polar'], ds['u_azimut'].isel(s_rho = sigma), cmax = cmax)
		#pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['rvorticity'].isel(s_rho = sigma)/ds['f'].mean(), cmax = 1e1, cmap = cmocean.cm.curl)
		pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['alpha'].isel(s_rho = sigma), cmax = np.pi, cmap = mpl.cm.twilight_shifted)
	elif not sigma and not flux:
		pu = axisfix(ax[0,0], dg['lon_u_polar'], dg['lat_u_polar'], ds['ubar_radial'], cmax = cmax)
		pv = axisfix(ax[0,1], dg['lon_v_polar'], dg['lat_v_polar'], ds['ubar_azimut'], cmax = cmax)
		#pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['rvorticity'].isel(s_rho = sigma)/ds['f'].mean(), cmax = 1e1, cmap = cmocean.cm.curl)
		pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['alphabar'], cmax = np.pi, cmap = mpl.cm.twilight_shifted)   
	
	elif flux:
		suptitle = "Transport"
		utext = r"$q_r$"
		vtext = "$q_{\theta}$"
		vorqlabel = "Transport " + "$(m^2s^{-1})$"
		pu = axisfix(ax[0,0], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['q_radial'], cmax = cmax)
		pv = axisfix(ax[0,1], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['q_azimut'], cmax = cmax)
		#pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['rvorticity'].isel(s_rho = sigma)/ds['f'].mean(), cmax = 1e1, cmap = cmocean.cm.curl)
		pw = axisfix(ax[0,2], dg['lon_psi_polar'], dg['lat_psi_polar'], ds['alphabar'], cmax = np.pi, cmap = mpl.cm.twilight_shifted)   
	
	ax[0,0].text(0.9, 0.05, "$u_r$", transform=ax[0,0].transAxes, size=8)
	ax[0,1].text(0.9, 0.05, r"$u_{\theta}$", transform=ax[0,1].transAxes, size=8)
	ax[0,2].text(0.9, 0.05, r"$ \alpha $", transform=ax[0,2].transAxes, size=8)

	cb = fig.colorbar(pu, ax = ax[0], location = "bottom", anchor = (0, -.05), shrink = 2/3, aspect = 60, fraction = 0.2, pad = .25)
	cb.ax.set_xlabel(vorqlabel, fontsize = 8)
	cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
	cb.outline.set_linewidth(0.25) 

	cb = fig.colorbar(pw, ax = ax[0], location = "bottom", anchor = (1, -4.875), shrink = 1/3, aspect = 30, fraction = 0.2, pad = .25)
	cb.ax.set_xlabel("Direction (rads)", fontsize = 8)
	cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
	cb.outline.set_linewidth(0.25) 

	fig.subplots_adjust(wspace = 0, hspace = 0) 
	#fig.suptitle( "$\sigma = {}$".format(sigma), y = 0.5) 
	#fig.suptitle (suptitle, y = 0.5) 	
	plt.savefig("{}.png".format(filename), dpi = 1200, bbox_inches = "tight")
	plt.close(fig)

def momvis(ds, filename = "mom", sigma = None, flux = 1):

#norm=colors.SymLogNorm(linthresh=1e-7, linscale=0.1, vmin=-1e-4, vmax=1e-4, base=10)       
	norm=colors.SymLogNorm(linthresh=1e-5, linscale=0.1, vmin=-1e-2, vmax=1e-2, base=10)        
	momentum_terms = ['accel','cor','hadv','fsco','hjvf','hvisc','kvrf','prsgrd','vadv','vjvf','vvisc','wbrk'] 
	
	if sigma:
		ds = ds.isel(s_rho = sigma) 
	if not sigma:
		print("using depth-averaged form...")
		momentum_terms = [ f for f in ds.variables if ( f.endswith("_bar") and (f not in ["sstr_bar","wrol_bar","zbeh_bar","zeta_bar","zetw_bar","zqsp_bar"]) ) ]

	fig, ax = plt.subplots(nrows = 4, ncols = 3, squeeze = True, figsize = (5.5,6.3), sharex = True, sharey = True, subplot_kw=dict(projection=proj))

	for k,m in enumerate(momentum_terms):
		axis = ax.flatten()[k]
		pm = axisfix(axis, dg['lon_psi_polar'], dg['lat_psi_polar'], ds[m]*flux, norm = norm)
		axis.text(0.025, 0.925, "{}".format(m), transform=axis.transAxes, size=6)

	cb = fig.colorbar(pm, ax = ax[-1,:], location = "bottom", anchor = (0.5, -.5), shrink = 0.96, aspect = 60, fraction = 0.2)
	cb.ax.tick_params(width = 0.25, length = 2, labelsize = 6)
	cb.outline.set_linewidth(0.25)  

	fig.subplots_adjust(wspace = -.1, hspace = 0)
	plt.savefig("{}.png".format(filename), dpi = 1200, bbox_inches = "tight")
	plt.close(fig)

def xgrid(ds):

	ds.rename({'eta_u': 'eta_rho', 'xi_v': 'xi_rho', 'xi_psi': 'xi_u', 'eta_psi': 'eta_v'})
	coords={'xi':{'center':'xi_rho', 'inner':'xi_u'}, 
			'eta':{'center':'eta_rho', 'inner':'eta_v'}, 
			's':{'center':'s_rho', 'outer':'s_w'}}

	grid = xgcm.Grid(ds, coords= coords, periodic = 'xi')
	return ds, grid

grid = False
for f in filepaths:
#for f in [filepaths[-4]]:
	print(f)
	cirname = f + '/avg26th.nc'
	swname = f + '/sw.nc'
	nmname = f + '/nm.nc'

	ds = xr.open_dataset(cirname, decode_times = False)
	if not grid:
		dc, grid = xgrid(ds)
	else:
		dc = ds
	metrics(dc, grid = grid)
	
	sw = xr.open_dataset(swname, decode_times = False) 
	nm = xr.open_dataset(nmname, decode_times = False)

	dc['u_radial'] = -dc.u_eastward*np.sin(dc.angle_psi) + dc.v_northward*np.cos(dc.angle_psi)
	dc['u_azimut'] = dc.u_eastward*np.cos(dc.angle_psi)  - dc.v_northward*np.sin(dc.angle_psi)

	dc['ubar_radial'] = -dc.ubar_eastward*np.sin(dc.angle_psi) + dc.vbar_northward*np.cos(dc.angle_psi)
	dc['ubar_azimut'] = dc.ubar_eastward*np.cos(dc.angle_psi)  - dc.vbar_northward*np.sin(dc.angle_psi)

	dc['q_radial'] = dc['h_psi']*dc.ubar_radial 
	dc['q_azimut'] = dc['h_psi']*dc.ubar_azimut 

#for sigma in [0,-1]: #surface and bottom levels
#   circvis(dc, filename = "{}/circ_σ={}".format(f,sigma), sigma = sigma)
#   for dm,label in zip([sw, nm],['sw','nm']): #plot streamwise and normal
#       momvis(dm, filename = "{}/{}_σ={}".format(f,label,sigma), sigma = sigma)
	for dm,label in zip([sw, nm],['sw','nm']): #plot streamwise and normal
		circvis(dc, filename = "{}/circ_barflux".format(f), cmax = 10, flux = True) 
		momvis(dm, filename = "{}/{}_barflux".format(f,label), flux = dc['h_psi']) 
