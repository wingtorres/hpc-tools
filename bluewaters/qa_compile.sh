#!/bin/bash
source ../coawst_config
module load nco
#cd COAWST

for i in {30} #loop through latitudes
do

dirname='ann_lat_'$(printf "%+.2d\n" $i) #name directory
echo "$dirname"

if [ ! -d "Output/$dirname" ]; then #create directory if doesn't exist
   mkdir Output/$dirname
   mkdir Output/${dirname}/Results
fi
   
   #change coriolis parameter (f) 
   ncap2 -s "where(f<1) f=2.0*0.0000729*sin($i*3.1415926535897932/180);" -O Projects/Annulus/Coupled/ann_grid.nc Projects/Annulus/Coupled/ann_grid.nc
#   ncks -v 'f' Projects/Annulus/Coupled/ann_grid.nc | more #how to view nc variable in text
   make clean
   ./coawst_ann.bash > compile.txt & #compile
   wait
   #cp coawstM Output/$dirname #move executable to output folder
   cp -a Projects/Annulus/Coupled/. Output/$dirname #copy all input/grid files to output folder
   sed -i "s#ocean_his_ann.nc#Output/${dirname}/Results/ocean_his_ann.nc#g" Output/${dirname}/ocean_ann.in #replace history file output location
   sed -i "s#ocean_dia_ann.nc#Output/${dirname}/Results/ocean_dia_ann.nc#g" Output/${dirname}/ocean_ann.in #replace diagnostics file output location 
   sed -i "s#ocean_avg_ann.nc#Output/${dirname}/Results/ocean_avg_ann.nc#g" Output/${dirname}/ocean_ann.in #replace averages file output location
   sed -i -- "s#Projects/Annulus/Coupled#Output/$dirname#g" Output/${dirname}/*.in #find and replace project file path in input files
done




