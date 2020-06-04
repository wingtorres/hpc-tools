import os
import numpy as np
import xarray as xr
from pycoawst.tools.circulation import swnmRotate, streamwise_normal, curv2cart, cart2swnm
from pycoawst.tools.grid import sigma2z, metrics
from pycoawst.visualization.plotting import showSlice
from pycoawst.tools.grid import cart2polar
from pycoawst.tools.operators import nctAvg

scratch = os.environ['MYSCRATCH']
group = os.environ['MYGROUP']

directory = scratch + "/doneski/"
filepaths = sorted([directory + f + '/results/' for f in os.listdir(directory) ])
additional = sorted([scratch + '/bluewaters/' + f + '/results/' for f in os.listdir(scratch + '/bluewaters/') ])
filepaths.extend(additional)
filepaths

start = 25*86400
finis = 26*86400

avgfile = "avg26th.nc"
diafile = "dia26th.nc"

for f in filepaths:

	print("Averaging {}...".format(f))
	dirname = f.split('/')[5]
	
	avglist = [f + ff for ff in sorted(os.listdir(f)) if ff.startswith('ocean_avg_ann')] #fetch average files
	dialist = [f + ff for ff in sorted(os.listdir(f)) if ff.startswith('ocean_dia_ann')] #fetch diagnos files

	avgout = "{}/{}".format(dirname,avgfile)
	diaout = "{}/{}".format(dirname,diafile)
	os.makedirs(dirname, exist_ok = True)

	nctAvg(start,finis,avglist,avgout)
	nctAvg(start,finis,dialist,diaout)
	  

