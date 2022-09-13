filenames=/work/wtorres/slope_2D_runs_nonperiodic/*

for f in $filenames
do

nogo="vbar_0.25"
if [[ $f != *$nogo* ]]; then
echo "Averaging $f ..."

relpath=$f/results
#ncra $relpath/ocean_avg_0021[789].nc $relpath/ocean_avg_002[234]* $relpath/ocean_avg.nc
python vrt_average.py $relpath $relpath/ocean_avg_0021[789].nc $relpath/ocean_avg_002[234]* 
fi

done
