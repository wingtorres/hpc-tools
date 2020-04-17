module load nco

projnames=/scratch/eot/torres/slope* 
#projnames=/scratch/eot/torres/smol*
compressdir=/scratch/eot/torres/compress
tempname=/scratch/eot/torres/temp/temp.nc
compname=/scratch/eot/torres/temp/comp.nc
for g in $projnames
do

#echo "Copying $g to $outdir ..."
#rsync -a --ignore-existing ${g} $compressdir --exclude=Build --exclude="/*/*/*" 
filenames=${g}/Results/*.nc

for f in $filenames
do

   outdir=$(echo $f | awk -F/ '{print $5}')
   outfile=$(echo $f | awk -F/ '{print $7}')
   avgstr="ocean_avg_ann" #only compress average files

   if [[ -f "${compressdir}/${outdir}/Results/${outfile}" ]]; then
      echo "skipping"
      continue
   fi   

   if [[ $outfile  == $avgstr* ]]; then
      echo "Averaging $f ..."  
      ncra -O --mro -d ocean_time,,,2,2 $f $tempname
      echo "Compressing $tempname ..."
      ncks -O -4 -L 1 $tempname ${compressdir}/${outdir}/Results/${outfile}
      echo "Transferred to ${compressdir}/${outdir}/Results/"
   else
      echo "Copying $f to ${compressdir}/${outdir}/Results/"
      cp $f ${compressdir}/${outdir}/Results/
   fi

done
done

#sandbox:
#/scratch/eot/torres/smol*
