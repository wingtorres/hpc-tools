module load python/3.6.2-anaconda-tensorflow
source activate lilac

#filenames=/work/wtorres/hs_100/reef*/Results/*116.nc
filenames=/work/wtorres/hs_100/reef_u_016_z0_0.0625/Results/ocean_avg_reef_0000*
for f in $filenames
do
  echo "Averaging $f ..."
  #outname=$(echo $f | awk -F/ '{print $5}')
   outname=$(echo $f | awk -F/ '{print $7}')
#ncra $f $outname'_avg.nc'
ncks -d s_rho,-1 $f "/work/wtorres/particles/surface_${outname}"
done
