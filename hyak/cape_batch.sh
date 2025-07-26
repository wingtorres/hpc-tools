#!/bin/bash
conda activate seakaunal

cppdef="CAPE_IDEALIZED"
export homeproj="/gscratch/nearshore/wtorres/opt/COAWST/Projects/cape_idealized"
export ogproj="/Users/wit/COAWST/Projects/rip_idealized"

#Computational
wavnodes=5
ocnnodes=35
export nprocs=$(($wavnodes + $ocnnodes))
export taskspernode=40
export nodes=$(($nprocs / $taskspernode))

#Time step and output
dt=2.0 #time step
nt=86400 #total time of simulation in seconds
ntimes=$(echo "$nt/$dt" | bc)
nhis=$(echo "3600/$dt" | bc)
ndefhis=$(echo "86400/$dt" | bc)
navg=$(echo "600/$dt" | bc)
ndefavg=$(echo "3600/$dt" | bc)

#submission loop

#for dTdz in 0.01 0.08 
#do

#for dSdz in 0 0.15
#do
#for Hs in 0.0 3.0 
#do
#for direction in 270 300
#do
#for amp in 0.0 1.5
#do
#for phi in 0.0 45.0
#do

dSdz=0.15
Hs=3.0
direction=300
amp=1.5
phi=45.0

dirname="dSdz_${dSdz}_Hs_${Hs}_dir_${direction}_amp_${amp}_phi_${phi}"
export coawstproj="/gscratch/nearshore/wtorres/output/cape/${dirname}"

#Copy directory over
if [ ! -d "$coawstproj" ]; then #create directory if doesn't exist
   mkdir ${coawstproj}
   mkdir ${coawstproj}/results
   cp -a ${homeproj}/. ${coawstproj} #copy all input/grid files to output folder
   wait ${!}
fi

echo "$coawstproj"

#Modify physical parameters
echo "modifying physical parameters"

#waves
sed -i "s#PAR.*#PAR ${Hs} 6.28 ${direction} 10.0#"

#initial stratification
sed -i "s#dSdz=.*#dSdz=${dSdz}_r8#" ${coawstproj}/ana_initial.h
## sed -i "s#dTdz=.*#dTdz=${dTdz}_r8#" ${coawstproj}/ana_initial.h 

#tidal amplitude
sed -i "s#amp=.*#amp=${amp}_r8#" ${coawstproj}/ana_fsobc.h
sed -i "s#amp=.*#amp=${amp}_r8#" ${coawstproj}/ana_initial.h

#Coriolis
ncap2 -s "f=f*0+2.0*0.0000729*sin(${phi}*3.1415926535897932/180);" -O ${homeproj}/roms_grid.nc ${coawstproj}/roms_grid.nc

#Bottom Drag
#sed -i "s#RDRG2 ==.*#RDRG2 ==${rdrg2}d0#" ${coawstproj}/ocean.in

#Modify computational parameters
echo "modifying computational parameters..."
sed -i "s#--nodes=.*#--nodes=${nodes}#" coawst_job.slurm
sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${coawstproj}/coupling.in
sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${coawstproj}/coupling.in
sed -i "s#NtileI ==.*#NtileI == 7#" ${coawstproj}/ocean.in
sed -i "s#NtileJ ==.*#NtileJ == 5#" ${coawstproj}/ocean.in

#Modify project input file names
echo "modifying input file names..."
sed -i "s#WAV_name =.*#WAV_name = ${coawstproj}/swan.in#" ${coawstproj}/coupling.in
sed -i "s#OCN_name =.*#OCN_name = ${coawstproj}/ocean.in#" ${coawstproj}/coupling.in
sed -i -- "s#${homeproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files
sed -i -- "s#${homeproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files

#Modify timestep & write output
echo "modifying timestep and output frequency..."
sed -i "s#DT ==.*#DT == ${dt}#" ${coawstproj}/ocean.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $ntimes#" ${coawstproj}/ocean.in #simulation duration
sed -i "s#NHIS ==.*#NHIS == $nhis#" ${coawstproj}/ocean.in #history output frequency
sed -i "s#NDEFHIS ==.*#NDEFHIS == $ndefhis#" ${coawstproj}/ocean.in #number time steps before new .nc file
sed -i "s#NAVG ==.*#NAVG == $navg#" ${coawstproj}/ocean.in #average output frequency
sed -i "s#NDEFAVG ==.*#NDEFAVG == $ndefavg#" ${coawstproj}/ocean.in
sed -i "s#NDIA ==.*#NDIA == $navg#" ${coawstproj}/ocean.in #diagnostic output frequency
sed -i "s#NDEFDIA ==.*#NDEFDIA == $ndefavg#" ${coawstproj}/ocean.in #number time steps before new .nc file

#Copy build script
echo "copying build script..."
cp /gscratch/nearshore/wtorres/opt/COAWST/build_coawst.sh ${coawstproj}/ #copy build script over
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${coawstproj}#" ${coawstproj}/build_coawst.sh #Change analytic + header dir
sed -i "s#COAWST_APPLICATION=.*#COAWST_APPLICATION=${cppdef}#" ${coawstproj}/build_coawst.sh
sed -i "s#VARNAME =.*#VARNAME = /gscratch/nearshore/wtorres/opt/COAWST/ROMS/External/varinfo.dat#" ${coawstproj}/ocean.in
chmod +x ${coawstproj}/build_coawst.sh #fix permissions

coawstcompile=$(sbatch --output=${coawstproj}/compile.out --error=${coawstproj}/compile.err --export=coawstproj=$coawstproj --parsable coawst_compile.slurm)

wait ${!}
sleep 1

sbatch --ntasks=$nprocs --ntasks-per-node=$taskspernode --nodes=$nodes \
--dependency=aftercorr:$coawstcompile \
--output=${coawstproj}/coawst.out --error=${coawstproj}/coawst.err --export=coawstproj=$coawstproj coawst_job.slurm

#sbatch --ntasks=$nprocs --ntasks-per-node=$taskspernode --nodes=$nodes \
#--output=${coawstproj}/coawst.out --error=${coawstproj}/coawst.err --export=coawstproj=$coawstproj coawst_job.slurm

wait ${!}
sleep 1

#done
