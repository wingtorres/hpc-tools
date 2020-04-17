#!/bin/bash
source /u/eot/torres/coawst_config
module load nco
#cd COAWST

#for i in {0..0..0} #{0,-30} #loop through latitude
#do
#for j in {1..1..0} #{1,10} #loop through z0 (cm)
#do
i=-30
j=1

kN=$(echo "$j*30/100" | bc -l)
kNstr=$(printf "%0.2f\n" $kN)
z0=$(echo "$j/100" | bc -l)
z0str=$(printf "%0.2f\n" $z0)
d50=$(echo "$j*30/2.5/100" | bc -l)
d50str=$(printf "%0.2f\n" $d50)

dirname='ann_lat_'$(printf "%+03d\n" $i)'_kn_'$(printf "%02g\n" $j) #name directory
export annproj="/scratch/eot/torres/${dirname}"
#export homeproj="Projects/Annulus/Barotropic"
export homeproj="/u/eot/torres/COAWST/Projects/Annulus/Barotropic"

#cp ${annproj}/Results/ocean_his_ann_00011.nc ${annproj}/ocean_ini_ann.nc #copy history file
#ncks -A -C -v temp,salt ${annproj}/ocean_rst.nc ${annproj}/Results/ocean_avg_ann_00003.nc
#ncks -A -C -v temp,salt ${annproj}/ocean_rst.nc ${annproj}/Results/ocean_his_ann_00011.nc
#cp ${annproj}/Results/ocean_his_ann_00011.nc ${annproj}/ocean_ini_ann.nc #copy history file
#ncks -A -v temp,salt ${annproj}/ocean_rst.nc ${annproj}/ocean_ini_ann.nc  #update w/ TS fields from restart

cp /scratch/eot/torres/ann_restart/Results/ocean_his_ann_00017.nc ${annproj}/ocean_ini_ann.nc #copy history file as restart
sed -i "s#NRREC == 0#NRREC == -1#" ${annproj}/ocean_ann.in #replace averages file output location
sed -i "s#ININAME ==.*#ININAME == ${annproj}/ocean_ini_ann.nc#" ${annproj}/ocean_ann.in

#anncompile=$(qsub -v annproj ann_compile.pbs)
qsub -e ${annproj}/ann.e -o ${annproj}/ann.o -v annproj annulus_job.pbs #-W depend=afterok:$anncompile annulus_job.pbs
wait ${!}
sleep 1

#done
#done




