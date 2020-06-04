import os
import numpy as np
import xarray as xr
import xgcm

from functions import enhanceDS, orientDS
from pycoawst.tools.grid import sigma2z, metrics
from pycoawst.tools.momentum import mom2swnm
from pycoawst.tools.grid import cart2polar
from pycoawst.tools.operators import nctAvg

#same function as avgdia2swnm but align to common time stamp

scratch = os.environ['MYSCRATCH']
group = os.environ['MYGROUP']

directory = scratch + "/doneski/"
filepaths = sorted([directory + f + '/results/' for f in os.listdir(directory) ])
filepaths

grdname = group + '/COAWST/Projects/Annulus/smol/ann_grid.nc' 
dg = xr.open_dataset(grdname)
dg['lon_u_polar'], dg['lat_u_polar'] = cart2polar( dg['x_u'], dg['y_u'])
dg['lon_v_polar'], dg['lat_v_polar'] = cart2polar( dg['x_v'], dg['y_v'])
dg['lon_psi_polar'], dg['lat_psi_polar'] = cart2polar( dg['x_psi'], dg['y_psi' ])
dg['lon_rho_polar'], dg['lat_rho_polar'] = cart2polar( dg['x_rho'], dg['y_rho' ])

start = 25*86400
finis = 26*86400

avgfile = "avg26th.nc"
diafile = "dia26th.nc"
swfile = "sw.nc"
nmfile = "nm.nc"

grid = False
coords={'xi':{'center':'xi_rho', 'inner':'xi_u'}, 
        'eta':{'center':'eta_rho', 'inner':'eta_v'}, 
         's':{'center':'s_rho', 'outer':'s_w'}}
   
for f in filepaths[-4:]:

	print("Averaging {}...".format(f))
	dirname = f.split('/')[5]
	
	avglist = [f + ff for ff in sorted(os.listdir(f)) if ff.startswith('ocean_avg_ann')] #fetch average files
	dialist = [f + ff for ff in sorted(os.listdir(f)) if ff.startswith('ocean_dia_ann')] #fetch diagnos files

	avgout = "{}/{}".format(dirname,avgfile)
	diaout = "{}/{}".format(dirname,diafile)
	nmout = "{}/{}".format(dirname,swfile)
	swout = "{}/{}".format(dirname,nmfile)
	
	os.makedirs(dirname, exist_ok = True)
	
	#find multifile lists within start < t < finis, but don't average yet
	avgdaylist = nctAvg(start,finis,avglist,avgout, average = False)
	diadaylist = nctAvg(start,finis,dialist,diaout, average = False)

	#load lists as multfile datasets
	ds_avgday = xr.open_mfdataset(avgdaylist, decode_times = True, parallel = True, combine = "by_coords", data_vars = 'minimal')
	ds_diaday = xr.open_mfdataset(diadaylist, decode_times = True, parallel = True, combine = "by_coords", data_vars = 'minimal')
   
	dc = orientDS(ds_avgday, dg)
	dm = orientDS(ds_diaday, dg)
	
	while grid is False:
		grid = xgcm.Grid(dc, coords= coords, periodic = 'xi')
	
	dc = enhanceDS(dc, grid = grid)

	#put on same time stamp
	dc = dc.resample(ocean_time="3H").mean()
	dm = dm.resample(ocean_time="3H").mean()

	dc.to_netcdf('circulation.nc')
	dm.to_netcdf('momentum.nc')
	assert(False)
	#streamwise normal rotation
	dsw, dnm, twonames, trinames = mom2swnm(dm, dc, grid) #convert to streamwise normal momentum budget

	#average over day
	dc.mean('ocean_time').to_netcdf(avgout)
	dsw.mean('ocean_time').to_netcdf(swout)
	dnm.mean('ocean_time').to_netcdf(nmout)
		
	assert(False)
