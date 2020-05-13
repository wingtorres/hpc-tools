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

#sed -i "s#VISC2 == [^ ]*#VISC2 == 0.5d0#" ${annproj}/ocean_ann.in

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

sed -i "s#GRDNAME ==.*#GRDNAME == ${annproj}/ann_grid.nc#" ${annproj}/ocean_ann.in #change ROMS grid path
sed -i "s#RSTNAME ==.*#RSTNAME == ${annproj}/ocean_rst_ann.nc#" ${annproj}/ocean_ann.in #replace restart file output location
sed -i "s#HISNAME ==.*#HISNAME == ${annproj}/results/ocean_his_ann.nc#" ${annproj}/ocean_ann.in #replace history file output location
sed -i "s#DIANAME ==.*#DIANAME == ${annproj}/results/ocean_dia_ann.nc#" ${annproj}/ocean_ann.in #replace diagnostics file output location 
sed -i "s#AVGNAME ==.*#AVGNAME == ${annproj}/results/ocean_avg_ann.nc#" ${annproj}/ocean_ann.in #replace averages file output location

rstfile=$(ls ${annproj}/results/ocean_his_* | tail -n 1)
#if [ ! -d "${annproj}/ocean_ini.nc" ]; then #create init file if doesn't exist
cp $rstfile ${annproj}/ocean_ini.nc #copy last history file as init file
#fi

if [ ! -d "${annproj}/results" ]; then
   mkdir ${annproj}/results
fi

#sed -i "/Restart name \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/a RESTART ${annproj}/swan_rst.dat FREE 3 HR" ${annproj}/swan_ann.in
#sed -i "/PROP BSBT/a INIT HOTSTART MULTIPLE '${annproj}/swan_rst.dat' " ${annproj}/swan_ann.in
sed -i "s#NRREC ==.*#NRREC == 4#" ${annproj}/ocean_ann.in #start new run initialized by restart
sed -i "s# ININAME ==.*# ININAME == ${annproj}/ocean_ini.nc#" ${annproj}/ocean_ann.in #specify ini file

sed -i "s#MY_ROOT_DIR=.*#MY_ROOT_DIR=${MYGROUP}/COAWST#" ${annproj}/coawst_ann.bash #change root before recompiling
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${annproj}#" ${annproj}/coawst_ann.bash #change path before recompiling
sed -i "s#VARNAME =.*#VARNAME = /group/pawsey0106/wtorres/COAWST/ROMS/External/varinfo.dat#" ${annproj}/ocean_ann.in
sed -i "s#define ANA_INITIAL#undef ANA_INITIAL#" ${annproj}/annulus.h
cp ${MYGROUP}/COAWST/hpc-tools/pawsey/coawstM_rst ${annproj}/coawstM #copy executable over

#anncompile=$(sbatch --output=${annproj}/compile.out --error=${annproj}/compile.err --export=annproj=$annproj --parsable ann_compile.sh)
#sbatch --dependency=afterok:$anncompile --output=${annproj}/ann.out --error=${annproj}/ann.err --export=annproj=${annproj} annulus_job.sh

wait

sbatch --ntasks=$totnodes --ntasks-per-node=$taskspernode --nodes=$nodes \
--output=${annproj}/ann.out --error=${annproj}/ann.err --export=annproj=$annproj annulus_job.sh

sleep 1

done




