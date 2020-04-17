import sys
import numpy as np
import xarray as xr
import cartopy.crs as crs
import matplotlib.pyplot as plt
from scipy.sparse import diags, kron, linalg

def streamfunction(vorticity, dx = 1, dy = 1): 

    m,n = vorticity.shape[0], vorticity.shape[1]

    em = [1]*(m-1)
    en = [1]*(n-1) 
    
    #Dirichlet on n = 0, Periodic on m = 0, m = m, Neumann on n = n

    diagonals = [ em , [-2]*(m),  em ]
    Dm = diags(diagonals, [-1,0,1])
    In = diags( [1]*(n), 0)
    
    diagonals = [ en , [-2]*(n),  en ]
    Dn = diags(diagonals, [-1,0,1])
    Im = diags( [1]*(m), 0)

    diagonals = [em[:] + [1] , em[:] + [1]]
    C = diags(diagonals, [-(n*m-m),(n*m-m)] )

    A = kron(In,Dm) + kron(Dn,Im) + C #this one
    
    b = vorticity.flatten('F')
    psi = linalg.cg(A,b, tol = 1e-6)[0].reshape(m, n, order = 'F')
    
    return psi 

def psiFig(filename, savename, cmin = -3/8, cmax = 3/8, proj = crs.Mercator(central_longitude=0.0, min_latitude=-0.5, max_latitude = 0.5) ):
   
   ds = xr.open_mfdataset(filename, decode_times = False, combine = "by_coords", parallel = True).mean('ocean_time')                 
   psi = streamfunction( np.squeeze(-ds.rvorticity_bar.values)  )
   ds['psi'] = ds.rvorticity_bar.copy()
   ds['psi'].values = np.reshape(psi, ds.rvorticity_bar.shape)
   
   levels = np.linspace(cmin, cmax, 100)
   ax = plt.axes(projection = proj)
#   ax.background_patch.set_facecolor('k')
   pc0 = ax.contour(ds.lon_psi, ds.lat_psi, psi, levels = levels, vmin = cmin, vmax = cmax, colors = 'k', linewidths = .125)
   pc0 = ax.contourf(ds.lon_psi, ds.lat_psi, psi, levels = levels, vmin = cmin, vmax = cmax, cmap = 'RdBu_r')
   #plt.tight_layout()
   savename = savename.replace(".","")
   plt.savefig(savename + ".png", dpi = 600) #facecolor ='k'

psiFig(sys.argv[1], sys.argv[2])
