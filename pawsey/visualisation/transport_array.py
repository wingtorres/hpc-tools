import os
import sys
import numpy as np
import pandas as pd
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

filepaths = sorted([f for f in os.listdir(group + "/hpc-tools/pawsey/visualisation/") if f.startswith("smol")])

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

coords={'xi':{'center':'xi_rho', 'inner':'xi_u'}, 
        'eta':{'center':'eta_rho', 'inner':'eta_v'}, 
		's':{'center':'s_rho', 'outer':'s_w'}}

#prepare dataframes
ds_U = pd.DataFrame(columns = lat, index = z0) #{}
ds_V = ds_U.copy()
ds_UV = ds_U.copy()

def transport(ds, dg, grid = None, sec=71):
	
	sec = 71
	u_azimut = grid.average(grid.integrate(ds.u,['s']),['xi']).isel(ocean_time = 0)
	u_azimut_masked = np.ma.masked_less_equal(u_azimut, 0)
	radius = np.hypot(dg.x_u,dg.y_u).mean('xi_u')

	v_radial = grid.integrate( (ds.v), ['s']).isel(eta_v = sec).isel(ocean_time = 0)
	v_radial_masked = np.ma.masked_less_equal(v_radial, 0)

	x_arc = dg.x_v.isel(eta_v = sec)
	y_arc = dg.y_v.isel(eta_v = sec)
	ang_radial = np.arctan2(x_arc,y_arc) - np.pi/2
	arc_radial = np.hypot(x_arc,y_arc)
	s = arc_radial*ang_radial/1e3

	U = np.trapz(u_azimut[sec:], radius[sec:])
	V = np.trapz(v_radial.clip(0), s*1e3)

	return U,V

grid = False
for f in filepaths:
	
	print(f)	
	ds = xr.open_dataset( "{}/avgplus.nc".format(f), decode_times = False)
	
	if not grid:
		grid = xgcm.Grid(ds, coords=coords, periodic = 'xi')
		metric = metrics(ds, grid = grid)
		grid = xgcm.Grid(ds, coords=coords, metrics = metric, periodic = 'xi')
	
	#identify z0/phi
	latstr = [s for s in lat if s in f.split('/')[-1]][0] 
	z0str =  [s for s in z0 if s in f.split('/')[-1]][0]
	#i = latdict[ latstr ]
	#j = z0dict[ z0str ]
	print("lat = {}\nz0 = {}".format(latstr,z0str))
	ds_U[latstr][z0str], ds_V[latstr][z0str] = transport(ds, dg, grid = grid) 
	ds_UV[latstr][z0str] = ds_U[latstr][z0str]/ds_V[latstr][z0str]
	#print(ds_U[i,j]/ds_V[i,j])

#df = pd.DataFrame.from_dict(ds_UV,orient = "index")
#df = pd.DataFrame.from_dict(ds_UV)
df = ds_UV.copy()
df.index.rename("z0",inplace = True)
df.reset_index(level=0,inplace=True)
df = pd.melt(df, id_vars = "z0", var_name = "latitude", value_vars =  lat, value_name = "U/V")
#df['latitude'] = df['latitude'].astype("category")
print(df)

fig, ax = plt.subplots()
ax.set_xscale('log')
sns.lineplot(x = "z0", y = "U/V", hue = "latitude", data = df.astype(float), legend = "full", ax = ax)
#sns.heatmap(df.astype(float)) #, annot = True)
plt.legend(fontsize="x-small", frameon = False)
fig.tight_layout()
fig.savefig('test.png')

#plt.savefig("{}.png".format(key), dpi = 1200, bbox_inches = "tight")
