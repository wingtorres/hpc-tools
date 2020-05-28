import os
import subprocess
import xarray as xr

def nctAvg(start,end,filelist,outfile):
	
	avgfiles = []
	
	for f in filelist:
		time = xr.open_dataset(f, decode_times = False).ocean_time.values

		if (time[-1] < end) and (time[0] > start):
				avgfiles.append(f)

	#let nco do the averaging (faster than xarray.resample("ocean_time"=24H).mean())
	command = ['ncra'] + avgfiles + outfile 
	subprocess.check_output(command)
	return filelist

#Example: find files that contain day 29-30
#scratch=os.environ['MYSCRATCH']
#projdir=scratch + '/doneski/smol_lat_-30_z0_016/results'
#filelist = [projdir + '/' + f for f in os.listdir(projdir) if f.startswith('ocean_avg_ann')]
#nctAvg(25*86400,26*86400,filelist)

#ds = xr.open_mfdataset(filelist, combine = "by_coords", parallel = True, decode_times = False).resample(ocean_time='24H').mean()
#ncra --mro -d ocean_time,,,2,2 -v vbar $filenames /scratch/eot/torres/temp/vbar.nc

