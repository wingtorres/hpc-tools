import os
import sys
import numpy as np
import xarray as xr
import holoviews as hv
import hvplot.xarray 
import matplotlib.pyplot as plt
import matplotlib.colors as colors

dirpath = sys.argv[1]

#find all average files after restart
files = sorted( ["{}{}".format(dirpath,f) for f in os.listdir(dirpath) if f.startswith("ocean_avg")] )
files_filt = [f for f in files if xr.open_dataset(f, decode_times = False).ocean_time.values[0]  > 14*24*3600 ]


#Create mf dataset
ds = xr.open_mfdataset(files_filt, decode_times = False, parallel = True, concat_dim = "ocean_time", combine ='by_coords')

#calculate transport
grdname = "/group/pawsey0106/wtorres/COAWST/Projects/Annulus/smol/ann_grid.nc"
dg = xr.open_dataset(grdname)
h_u = dg.h.interp(xi_rho = ds.xi_u, eta_rho = ds.eta_u).drop(["xi_rho","eta_rho"])
h_v = dg.h.interp(xi_rho = ds.xi_v, eta_rho = ds.eta_v).drop(["xi_rho","eta_rho"])
ds["q_u"] = h_u*ds.ubar
ds["q_v"] = h_v*ds.vbar

dc, grid = xgrid(ds)
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

#create html visualization
fig = ( ds.isel(ocean_time = slice(0,-1,100)).q_u.hvplot.quadmesh(x = "lon_u", y="lat_u", cmap = "RdBu", dynamic = True,
                                                              project = True, rasterize = True, clim = (-15, 15))
      + ds.isel(ocean_time = slice(0,-1,100)).q_v.hvplot.quadmesh(x = "lon_v", y="lat_v", cmap = "RdBu", dynamic = True,
                                                              project = True, rasterize = True, clim = (-15, 15))
      )

hv.save(fig, "test2.gif", fps = 5) #, fmt = "gif")
