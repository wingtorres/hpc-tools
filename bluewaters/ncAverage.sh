module load nco
filenames=/scratch/eot/torres/smol_lat_-30_z0_0.25/Results/ocean_avg_ann_00*.nc

ncra --mro -d ocean_time,,,2,2 -v vbar $filenames /scratch/eot/torres/temp/vbar.nc

#for f in $filenames
#do
#  echo "Averaging $f ..."
#  outname=$(echo $f | awk -F/ '{print $6}')
#ncra $f $outname'_avg.nc'
#ncks -d s_rho,-1 $f "/work/wtorres/particles/surface_${outname}"
#ncra -d ocean_time,,,2,2 --mro $f /scratch/eot/torres/temp/u_${outname}

#done


