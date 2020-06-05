import xarray as xr

from pycoawst.tools.momentum import mom2swnm
from pycoawst.tools.circulation import streamwise_normal, lagrangianVelocity
from pycoawst.tools.grid import sigma2z, metrics
from pycoawst.visualization.plotting import showSlice
from pycoawst.tools.grid import cart2polar
from pycoawst.tools.operators import nctAvg

def enhanceDS(ds, grid = None): 
    
   #add z_rho, z_w   
   sigma2z(ds, vcoord = 's_w')
   sigma2z(ds, vcoord = 's_rho')
    
   #rotate with CCW and find streamwise-normal magnitude and angle
   ds = lagrangianVelocity(ds, grid = grid)
   ds = streamwise_normal(ds, grid = grid)
   
	#ds['u'] *= -1
   #ds['ubar'] *= -1
   #ds['u_stokes'] *= -1

   #derived quantities
   ds['rvorticity_normalized'] = ds.rvorticity_bar/ds['f'].values.mean()
   return ds

def orientDS(ds, dg):

   #no redundant coords
   ds = ds.rename({'eta_u': 'eta_rho', 'xi_v': 'xi_rho', 'xi_psi': 'xi_u', 'eta_psi': 'eta_v'})

   #send to the poles!
   ds['lon_u_polar'], ds['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
   ds['lon_v_polar'], ds['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
   ds['lon_psi_polar'], ds['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
   ds['lon_rho_polar'], ds['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])
   return ds
