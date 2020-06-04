import os
import numpy as np
import xarray as xr
import xgcm

from pycoawst.tools.momentum import mom2swnm
from pycoawst.tools.circulation import swnmRotate, streamwise_normal, curv2cart, cart2swnm, lagrangianVelocity
from pycoawst.tools.grid import sigma2z, metrics
from pycoawst.visualization.plotting import showSlice
from pycoawst.tools.grid import cart2polar
from pycoawst.tools.operators import nctAvg

scratch = os.environ['MYSCRATCH']
group = os.environ['MYGROUP']

filepaths = sorted([f for f in os.listdir(group + "/COAWST/hpc-tools/pawsey/visualisation/") if f.startswith("smol")])
grdname = group + '/COAWST/Projects/Annulus/smol/ann_grid.nc' 
dg = xr.open_dataset(grdname)
dg['lon_u_polar'], dg['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
dg['lon_v_polar'], dg['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
dg['lon_psi_polar'], dg['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
dg['lon_rho_polar'], dg['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])

def orientDS(ds, dg):
	
	#no redundant coords
	ds = ds.rename({'eta_u': 'eta_rho', 'xi_v': 'xi_rho', 'xi_psi': 'xi_u', 'eta_psi': 'eta_v'})

	#send to the poles!
	ds['lon_u_polar'], ds['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
	ds['lon_v_polar'], ds['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
	ds['lon_psi_polar'], ds['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
	ds['lon_rho_polar'], ds['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])
	return ds

def enhanceDS(ds, grid = None): 
		
	#add z_rho, z_w	
	sigma2z(ds, vcoord = 's_w')
	sigma2z(ds, vcoord = 's_rho')
		
	#rotate with CCW and find streamwise-normal magnitude and angle
	ds = lagrangianVelocity(ds, grid = grid)
	ds = streamwise_normal(ds, grid = grid)
	ds['u'] *= -1
	ds['ubar'] *= -1
	ds['u_stokes'] *= -1

	#derived quantities
	ds['rvorticity_normalized'] = ds.rvorticity_bar/ds['f'].values.mean()
	return ds

avfile = "avgplus.nc"
swfile = "sw.nc"
nmfile = "nm.nc"

grid = False
coords={'xi':{'center':'xi_rho', 'inner':'xi_u'}, 
        'eta':{'center':'eta_rho', 'inner':'eta_v'}, 
		   's':{'center':'s_rho', 'outer':'s_w'}}

for f in filepaths:

	da = xr.open_dataset(f + "/dia26th.nc", decode_times = False)
	dm = xr.open_dataset(f + "/avg26th.nc", decode_times = False)
	da = orientDS(da, dg)
	dm = orientDS(dm, dg)
	
	while grid is False:
		grid = xgcm.Grid(da, coords= coords, periodic = 'xi')
	
	da = enhanceDS(da, grid = grid)

	dsw, dnm, twonames, trinames = mom2swnm(dm, da, grid) #convert to streamwise normal momentum budget
	
	avout = "{}/{}".format(f,avfile)
	swout = "{}/{}".format(f,swfile)
	nmout = "{}/{}".format(f,nmfile)
	print( "writing {}, {}, {}...".format(avout,swout,nmout) )
	
	da.to_netcdf(avout)
	dsw.to_netcdf(swout)
	dnm.to_netcdf(nmout)

