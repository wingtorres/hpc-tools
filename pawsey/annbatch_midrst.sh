#!/bin/bash
projdir=${MYSCRATCH}/pawsey/*

wavnodes=16
ocnnodes=80
totnodes=$(($wavnodes + $ocnnodes))
taskspernode=24
nodes=$(($totnodes / $taskspernode))

for f in $projdir
do

export annproj=$f
#export annproj=/scratch/pawsey0106/wtorres/pawsey/smol_lat_-30_z0_01
echo "$annproj"

sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${annproj}/coupling_ann.in
sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${annproj}/coupling_ann.in
sed -i "s#NtileI ==.*#NtileI == 4#" ${annproj}/ocean_ann.in
sed -i "s#NtileJ ==.*#NtileJ == 20#" ${annproj}/ocean_ann.in 

sed -i "s#WAV_name =.*#WAV_name = ${annproj}/swan_ann.in#" ${annproj}/coupling_ann.in
sed -i "s#OCN_name =.*#OCN_name = ${annproj}/ocean_ann.in#" ${annproj}/coupling_ann.in

sed -i "s#READGRID COORDINATES 1 .*#READGRID COORDINATES 1 '${annproj}/ann_coord.grd' 4 0 0 FREE#" ${annproj}/swan_ann.in #change wave grid path
sed -i "s#READINP BOTTOM.*#READINP BOTTOM 1 '${annproj}/ann_bathy.bot' 4 0 FREE#" ${annproj}/swan_ann.in #change wave bathymetry path
sed -i "s#COMPUTE NONSTATIONARY.*#COMPUTE NONSTATIONARY 20000114.060000 600 SEC 20000201.000000#" ${annproj}/swan_ann.in #change to 30 day run


dt=2 #time step
nt=1447200 #total time of simulation in seconds
sed -i "s#DT ==.*#DT == ${dt}#" ${annproj}/ocean_ann.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $((nt / dt))#" ${annproj}/ocean_ann.in #simulation duration
sed -i "s#NHIS ==.*#NHIS == $((10800 / dt))#" ${annproj}/ocean_ann.in #history output frequency
sed -i "s#NDEFHIS ==.*#NDEFHIS == $((86400 / dt))#" ${annproj}/ocean_ann.in #number time steps before new .nc file
sed -i "s#NDIA ==.*#NDIA == $((10800 / dt))#" ${annproj}/ocean_ann.in #diagnostic output frequency
sed -i "s#NDEFDIA ==.*#NDEFDIA == $((86400 / dt))#" ${annproj}/ocean_ann.in #number time steps before new .nc file
sed -i "s#NAVG ==.*#NAVG == $((600 / dt))#" ${annproj}/ocean_ann.in #average output frequency
sed -i "s#NDEFAVG ==.*#NDEFAVG == $((7200 / dt))#" ${annproj}/ocean_ann.in

rstfile=${annproj}/results/ocean_his_00014.nc
cp $rstfile ${annproj}/ocean_ini.nc #copy history file to init file

sed -i "s#NRREC ==.*#NRREC == 4#" ${annproj}/ocean_ann.in #start new run initialized by restart

wait

#sbatch --ntasks=$totnodes --ntasks-per-node=$taskspernode --nodes=$nodes \
#--output=${annproj}/ann.out --error=${annproj}/ann.err --export=annproj=$annproj annulus_job.sh

sleep 1

done




