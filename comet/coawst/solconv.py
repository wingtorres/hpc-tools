import sys
import numpy as np
import netCDF4 as nc4


ds = nc4.Dataset('ocean_his_stokes.nc')
print(ds)
#u = np.array(ds.variables['u'][:,:,:]) #+ 149; 
v = np.array(ds.variables['v'][:,:,:]) #+ 149; 
t = np.array(ds.variables['ocean_time'][:])

u_t = np.diff(u,axis = 2)
v_t = np.diff(v,axis = 2)
mt = np.diff(t)

#u_t = np.ma.array(un,mask=np.isnan(u_t)) 
un = np.linalg.norm(u_t,axis=[0,1])

print(un)

