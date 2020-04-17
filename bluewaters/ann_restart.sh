#!/bin/bash
source /u/eot/torres/coawst_config
module load nco
#cd ~/COAWST

i=0

dirname='ann_restart' #name directory
export annproj="/scratch/eot/torres/${dirname}"
export homeproj="/u/eot/torres/COAWST/Projects/Annulus/Restart"

if [ ! -d "$annproj" ]; then #create directory if doesn't exist
   mkdir ${annproj}
   mkdir ${annproj}/Results
   cp -a ${homeproj}/. ${annproj} #copy all input/grid files to output folder
   cp ../coawst_ann.bash ${annproj}
   wait ${!}
fi

#Change analytic + header dir
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${annproj}#" ${annproj}/coawst_ann.bash

#change coriolis parameter (f) 
ncap2 -s "f=f*0+2.0*0.0000729*sin($i*3.1415926535897932/180);" -O ${homeproj}/ann_grid.nc ${annproj}/ann_grid.nc

sed -i "s#ocean_rst.nc#${annproj}/ocean_rst.nc#" ${annproj}/ocean_ann.in #replace restart file output location
sed -i "s#ocean_his_ann.nc#${annproj}/Results/ocean_his_ann.nc#" ${annproj}/ocean_ann.in #replace history file output location
sed -i "s#ocean_dia_ann.nc#${annproj}/Results/ocean_dia_ann.nc#" ${annproj}/ocean_ann.in #replace diagnostics file output location 
sed -i "s#ocean_avg_ann.nc#${annproj}/Results/ocean_avg_ann.nc#" ${annproj}/ocean_ann.in #replace averages file output location
#   sed -i "s#${homeproj}/ocean_flt_ann.nc#${annproj}/Results/ocean_flt_ann.nc#" ${annproj}/ocean_ann.in #replace floats file output location
sed -i -- "s#${homeproj}#${annproj}#g" ${annproj}/*.in #find and replace project file path in input files

if [ ! -f "${annproj}/coawstM" ]; then #test if compilation successful
   anncompile=$(qsub -e ${annproj}/compile.e -o ${annproj}/compile.o -v annproj ~/COAWST/Scripts/ann_compile.pbs)
   qsub -e ${annproj}/ann.e -o ${annproj}/ann.o -v annproj -W depend=afterok:$anncompile annulus_job.pbs
   wait ${!}
   sleep 1
fi





