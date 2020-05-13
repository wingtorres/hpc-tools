import os
import subprocess
import xarray as xr

scratch=os.environ['MYSCRATCH']
projdir=scratch + '/bluewaters/smol_lat_-30_z0_016/results'
#find files that contain day 29-30
filelist = []
for f in os.listdir(projdir):
   
   if not f.startswith('ocean_avg_ann'):
      continue

   time = xr.open_dataset(projdir+'/'+f, decode_times = False).ocean_time.values
   if (time[-1] < 30*3600*24) and (time[0] > 29*3600*24):
      filelist.append(projdir+'/'+f)

print(filelist)

command = ['ncra'] + filelist + ['out.nc']
subprocess.check_output(command)

#subprocess.Popen(['ncra'] + filelist + ['out.nc'])

#ncra --mro -d ocean_time,,,2,2 -v vbar $filenames /scratch/eot/torres/temp/vbar.nc

#for f in $filenames
#do
#  echo "Averaging $f ..."
#  outname=$(echo $f | awk -F/ '{print $6}')
#ncra $f $outname'_avg.nc'
#ncks -d s_rho,-1 $f "/work/wtorres/particles/surface_${outname}"
#ncra -d ocean_time,,,2,2 --mro $f /scratch/eot/torres/temp/u_${outname}

#done


