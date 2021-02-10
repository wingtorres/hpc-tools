#!/bin/bash
# Job submission loop for reef toy problem
#cd /home/wtorres/COAWST/Scripts

cppdef="SLOPE"
export homeproj="/home/wtorres/COAWST/Projects/slope/frustrum"

wavnodes=0
ocnnodes=40
export nprocs=$(($wavnodes + $ocnnodes))
export taskspernode=20
export nodes=$(($nprocs / $taskspernode))

dt=0.125 #time step
nt=864000 #total time of simulation in seconds
ntimes=$(echo "$nt/$dt" | bc)
nhis=$(echo "3600/$dt" | bc)
ndefhis=$(echo "43200/$dt" | bc)
navg=$(echo "300/$dt" | bc)
ndefavg=$(echo "3600/$dt" | bc)
vbar=0.125

#submission loop
for rdrg2 in 0.0625 0.125 0.25
do
for slope in 0.1 0.05 0.01
do
for lat in -30.0 -15.0 -1.0
do

dirname="cd_${rdrg2}_slope_${slope}_lat_${lat}_vbar_${vbar}"
export coawstproj="/work/wtorres/slope_2D_runs/${dirname}"

sed -i "s#define ANA_INITIAL#undef ANA_INITIAL#" ${coawstproj}/slope.h #recompile without ANA_INITIAL
sed -i "s#NRREC == 0#NRREC == -1#" ${coawstproj}/ocean.in #replace averages file output location
sed -i "s#ININAME ==.*#ININAME == ${coawstproj}/results/ocean_rst.nc#" ${coawstproj}/ocean.in #make ini file restart file

coawstcompile=$(qsub -e ${coawstproj}/compile.e -o ${coawstproj}/compile.o -v coawstproj coawst_compile.pbs)
qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj,nprocs,taskspernode,nnodes -W depend=afterok:$coawstcompile roms_job.pbs
wait ${!}
sleep 1

done
done
done
