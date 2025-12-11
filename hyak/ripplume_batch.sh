#!/bin/bash

cppdef="RIP_IDEALIZED"
export homeproj="/mmfs1/home/wtorres/rip_idealized"
export ogproj="Projects/rip_idealized"
wavnodes=5
ocnnodes=75
export nprocs=$(($wavnodes + $ocnnodes))
export taskspernode=40
export nodes=$(($nprocs / $taskspernode))

dt=0.25 #time step
nt=345600 #total time of simulation in seconds
ntimes=$(echo "$nt/$dt" | bc)
nhis=$(echo "3600/$dt" | bc)
ndefhis=$(echo "86400/$dt" | bc)
navg=$(echo "300/$dt" | bc)
ndefavg=$(echo "3600/$dt" | bc)

#submission loop

for dTdz in 0.0 0.01 0.02 0.04 0.08 0.16 0.32 0.64 
#for dTdz in 0.01 0.08 
do

#dTdz=0.64

dirname="dTdz_${dTdz}"
export coawstproj="/gscratch/nearshore/wtorres/${dirname}"
echo "$coawstproj"

if [ ! -d "$coawstproj" ]; then #create directory if doesn't exist
   mkdir ${coawstproj}
   #cp -a ${homeproj}/. ${coawstproj} #copy all input/grid files to output folder
   wait ${!}
fi

rsync -a --exclude=.git ${homeproj}/ ${coawstproj}/

#Modify physical parameters

#sed -i "s#RDRG2 ==.*#RDRG2 ==${rdrg2}d0#" ${coawstproj}/ocean.in
sed -i "s#dTdz=.*#dTdz=${dTdz}_r8#" ${coawstproj}/ana_initial.h

#Modify computational
sed -i "s#--nodes=.*#--nodes=${nodes}#" coawst_job.slurm
sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${coawstproj}/coupling.in
sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${coawstproj}/coupling.in
sed -i "s#NtileI ==.*#NtileI == 15#" ${coawstproj}/ocean.in
sed -i "s#NtileJ ==.*#NtileJ == 5#" ${coawstproj}/ocean.in

sed -i "s#WAV_name =.*#WAV_name = ${coawstproj}/swan.in#" ${coawstproj}/coupling.in
sed -i "s#OCN_name =.*#OCN_name = ${coawstproj}/ocean.in#" ${coawstproj}/coupling.in

sed -i "s#DT ==.*#DT == ${dt}#" ${coawstproj}/ocean.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $ntimes#" ${coawstproj}/ocean.in #simulation duration
sed -i "s#NHIS ==.*#NHIS == $nhis#" ${coawstproj}/ocean.in #history output frequency
sed -i "s#NDEFHIS ==.*#NDEFHIS == $ndefhis#" ${coawstproj}/ocean.in #number time steps before new .nc file
sed -i "s#NAVG ==.*#NAVG == $navg#" ${coawstproj}/ocean.in #average output frequency
sed -i "s#NDEFAVG ==.*#NDEFAVG == $ndefavg#" ${coawstproj}/ocean.in
sed -i "s#NDIA ==.*#NDIA == $navg#" ${coawstproj}/ocean.in #diagnostic output frequency
sed -i "s#NDEFDIA ==.*#NDEFDIA == $ndefavg#" ${coawstproj}/ocean.in #number time steps before new .nc file

sed -i -- "s#${ogproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files
sed -i -- "s#${homeproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files

cp /gscratch/nearshore/wtorres/opt/COAWST/build_coawst.sh ${coawstproj}/build_coawst.sh #copy build script over
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${coawstproj}#" ${coawstproj}/build_coawst.sh #Change analytic + header dir
sed -i "s#COAWST_APPLICATION=.*#COAWST_APPLICATION=${cppdef}#" ${coawstproj}/build_coawst.sh
sed -i "s#VARNAME =.*#VARNAME = /gscratch/nearshore/wtorres/opt/COAWST/ROMS/External/varinfo.dat#" ${coawstproj}/ocean.in
chmod +x ${coawstproj}/build_coawst.sh #fix permissions


##Compile and Run

#coawstcompile=$(sbatch --output=${coawstproj}/compile.out --error=${coawstproj}/compile.err --export=coawstproj=$coawstproj --parsable coawst_compile.slurm)

#wait ${!}
#sleep 1

#sbatch --ntasks=$nprocs --ntasks-per-node=$taskspernode --nodes=$nodes \
#--dependency=aftercorr:$coawstcompile \
#--output=${coawstproj}/coawst.out --error=${coawstproj}/coawst.err --export=coawstproj=$coawstproj coawst_job.slurm

#Run Only

sbatch --ntasks=$nprocs --ntasks-per-node=$taskspernode --nodes=$nodes \
--output=${coawstproj}/coawst.out --error=${coawstproj}/coawst.err --export=coawstproj=$coawstproj coawst_job.slurm


wait ${!}
sleep 1

done



