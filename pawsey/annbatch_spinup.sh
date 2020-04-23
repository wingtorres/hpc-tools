#!/bin/bash
projdir=${MYSCRATCH}/barotropic/*

wavnodes=16
ocnnodes=80
totnodes=$(($wavnodes + $ocnnodes))
taskspernode=24
nodes=$(($totnodes / $taskspernode))

for f in $projdir
do

export annproj=$f
#export annproj=/scratch/pawsey0106/wtorres/barotropic/smol_lat_-30_z0_0.0625
echo "$annproj"

sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${annproj}/coupling_ann.in #number of waves nodes
sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${annproj}/coupling_ann.in #number of ocean nodes
sed -i "s#NtileI ==.*#NtileI == 4#" ${annproj}/ocean_ann.in #tiling
sed -i "s#NtileJ ==.*#NtileJ == 20#" ${annproj}/ocean_ann.in #tiling

sed -i "s#WAV_name =.*#WAV_name = ${annproj}/swan_ann.in#" ${annproj}/coupling_ann.in #change swan input file name
sed -i "s#OCN_name =.*#OCN_name = ${annproj}/ocean_ann.in#" ${annproj}/coupling_ann.in #change ocean input file name

#sed -i "/Restart name \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/a RESTART ${annproj}/swan_rst.dat FREE 3 HR" ${annproj}/swan_ann.in
sed -i "s#READGRID COORDINATES 1 .*#READGRID COORDINATES 1 '${annproj}/ann_coord.grd' 4 0 0 FREE#" ${annproj}/swan_ann.in #change wave grid path
sed -i "s#READINP BOTTOM  1.*#READINP BOTTOM 1 '${annproj}/ann_bathy.bot' 4 0 FREE#" ${annproj}/swan_ann.in #change wave bathymetry path
sed -i "s#COMPUTE NONSTATIONARY 20000101.000000 600 SEC.*#COMPUTE NONSTATIONARY 20000101.000000 600 SEC 20000112.000000#" ${annproj}/swan_ann.in #change to 30 day run

dt=1 #time step
nt=1080000 #total time of simulation in seconds
sed -i "s#DT ==.*#DT == ${dt}#" ${annproj}/ocean_ann.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $((nt / dt))#" ${annproj}/ocean_ann.in #change simulation time
sed -i "s#NHIS ==.*#NHIS == $((10800 / dt))#" ${annproj}/ocean_ann.in
sed -i "s#NDEFHIS ==.*#NDEFHIS == $((86400 / dt))#" ${annproj}/ocean_ann.in
sed -i "s#NDIA ==.*#NDIA == $((10800 / dt))#" ${annproj}/ocean_ann.in
sed -i "s#NDEFDIA ==.*#NDEFDIA == $((86400 / dt))#" ${annproj}/ocean_ann.in 
sed -i "s#NAVG ==.*#NAVG == $((600 / dt))#" ${annproj}/ocean_ann.in
sed -i "s#NDEFAVG ==.*#NDEFAVG == $((7200 / dt))#" ${annproj}/ocean_ann.in

sed -i "s#GRDNAME ==.*#GRDNAME == ${annproj}/ann_grid.nc#" ${annproj}/ocean_ann.in #change ROMS grid path
sed -i "s#RSTNAME ==.*#RSTNAME == ${annproj}/ocean_rst_ann.nc#" ${annproj}/ocean_ann.in #replace restart file output location
sed -i "s#HISNAME ==.*#HISNAME == ${annproj}/results/ocean_his_ann.nc#" ${annproj}/ocean_ann.in #replace history file output location
sed -i "s#DIANAME ==.*#DIANAME == ${annproj}/results/ocean_dia_ann.nc#" ${annproj}/ocean_ann.in #replace diagnostics file output location 
sed -i "s#AVGNAME ==.*#AVGNAME == ${annproj}/results/ocean_avg_ann.nc#" ${annproj}/ocean_ann.in #replace averages file output location

if [ ! -d "${annproj}/results" ]; then
   mkdir ${annproj}/results
fi

sed -i "s#MY_ROOT_DIR=.*#MY_ROOT_DIR=${MYGROUP}/COAWST#" ${annproj}/coawst_ann.bash #change root before recompiling
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${annproj}#" ${annproj}/coawst_ann.bash #change path before recompiling
sed -i "s#VARNAME =.*#VARNAME = /group/pawsey0106/wtorres/COAWST/ROMS/External/varinfo.dat#" ${annproj}/ocean_ann.in
cp ${MYGROUP}/COAWST/hpc-tools/pawsey/coawstM ${annproj}/coawstM #copy executable over

#anncompile=$(sbatch --output=${annproj}/compile.out --error=${annproj}/compile.err --export=annproj=$annproj --parsable ann_compile.sh)
#sbatch --dependency=afterok:$anncompile --output=${annproj}/ann.out --error=${annproj}/ann.err --export=annproj=${annproj} annulus_job.sh

sbatch --ntasks=$totnodes --ntasks-per-node=$taskspernode --nodes=$nodes \
--output=${annproj}/ann.out --error=${annproj}/ann.err --export=annproj=$annproj annulus_job.sh

wait ${!}
sleep 1
done



