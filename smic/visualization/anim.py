import os
import sys
import xarray as xr
import xgcm
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import seaborn as sns
import cmocean

sys.path.append("/home/wtorres/functions/")
sys.path.append("/home/wtorres/functions/pycoawst")

from pycoawst.tools.grid import recoord, metrics


plt.rcParams['text.usetex'] = False
proj = ccrs.NorthPolarStereo()

resultsdir = "/work/wtorres/annulus_thermal-test/Results/"
diapaths = sorted([resultsdir+f for f in os.listdir(resultsdir) if f.startswith("ocean_dia")])
avgpaths = sorted([resultsdir+f for f in os.listdir(resultsdir) if f.startswith("ocean_avg")])

kwargs = {"combine": "by_coords", "data_vars": "minimal", "coords": "minimal", "compat": "override",  "preprocess": recoord, "parallel": True}
da = xr.open_mfdataset(avgpaths, decode_times = False, **kwargs)
dd = xr.open_mfdataset(diapaths, decode_times = False, **kwargs)
dg = xr.open_dataset("/work/wtorres/annulus_thermal-test/analytic_grid.nc")

coords={'xi':{'center':'xi_rho', 'inner':'xi_u'}, 
        'eta':{'center':'eta_rho', 'inner':'eta_v'}}
grid = xgcm.Grid(da, coords=coords, periodic = "xi")
metric = metrics(da, grid = grid, vertical = False)
grid = xgcm.Grid(da, coords=coords, metrics = metric, periodic = "xi")

#Kinematics movie
k = -1
kwargs = {"transform": ccrs.PlateCarree(), "add_colorbar": False}
cbar_kwargs = {"orientation": "horizontal", "pad": .15} #, "label": None, "labelsize": 4}

fig,axes = plt.subplots(1,3,sharex=True,sharey=True,figsize = (10.5,6), subplot_kw=dict(projection=proj))

pu = da.isel(ocean_time=0).ubar.plot(ax=axes[0], x = "lon_u", y = "lat_u", cmap = cmocean.cm.balance, vmin = -.1, vmax = .1, **kwargs)
pv = da.isel(ocean_time=0).vbar.plot(ax=axes[1], x = "lon_v", y = "lat_v", cmap = cmocean.cm.balance, vmin = -.1, vmax = .1, **kwargs)
pt = da.isel(ocean_time=0, s_rho = -1).temp.plot(ax=axes[2], x = "lon_rho", y = "lat_rho", cmap = cmocean.cm.tarn, vmin = 30-1, vmax = 30+1, **kwargs)
fig.colorbar(pu, ax=axes[0], orientation = "horizontal", label = "Velocity")
fig.colorbar(pv, ax=axes[1], orientation = "horizontal", label = "Velocity")
fig.colorbar(pt, ax=axes[2], orientation = "horizontal", label = "Temperature")
sns.despine(fig)

for ax in axes:
	ax.set_extent([-15,15,89.825,89.9125], ccrs.PlateCarree())
	ax.set_title("")

for k,time in enumerate(da.ocean_time):
	print(f"{k}/{len(da.ocean_time)}")
	pu.set_array(da.isel(ocean_time=k).ubar.values.ravel())
	pv.set_array(da.isel(ocean_time=k).vbar.values.ravel())
	pt.set_array(da.isel(ocean_time=k, s_rho = -1).temp.values.ravel())
	fig.suptitle(f"{time.values} seconds", y = 1.05)
	fig.savefig(f"kinematics_{k:03d}.png")

