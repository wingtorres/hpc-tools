import sys
import xarray as xr

import pycoawst.tools.grid as pcg
import pycoawst.tools.circulation as pcc

savepath = sys.argv[1]
filenames = sys.argv[2:]

path = savepath.replace("/","_").split("_") 
cd = float([path[k+1] for k,s in enumerate(path) if s == "cd"][0])

kwargs = {"combine": "by_coords", "data_vars": "minimal", "coords": "minimal", "compat": "override", "preprocess": pcg.recoord, "parallel": True, "use_cftime": True}
ds = xr.open_mfdataset(filenames, **kwargs)
ds, grid = pcg.xromsgrid(ds, vertical = False)
ds = pcc.strain_tensor(ds, grid)
ds = pcc.streamwise_normal(ds, grid, vertical = False)
ds = pcc.velocity_rho(ds,grid)
ds = pcc.shear_orbital(ds)
ds = pcc.volume_budget(ds, grid)
ds = pcc.vorticity_sn(ds, grid, cd)

ds.mean("ocean_time").to_netcdf(f"{savepath}/ocean_avg.nc")
