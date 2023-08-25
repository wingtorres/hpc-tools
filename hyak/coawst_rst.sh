#!/bin/bash

export homeproj="/mmfs1/home/wtorres/rip_idealized"
export ogproj="/Users/wit/COAWST/Projects/rip_idealized"
export coawstproj=/gscratch/nearshore/wtorres/results/rip_plumes/dTdz_0.64

wavnodes=5
ocnnodes=75
export nprocs=$(($wavnodes + $ocnnodes))
export taskspernode=40
export nodes=$(($nprocs / $taskspernode))

#sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${coawstproj}/coupling.in
#sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${coawstproj}/coupling.in
#sed -i "s#NtileI ==.*#NtileI == 15#" ${coawstproj}/ocean.in
#sed -i "s#NtileJ ==.*#NtileJ == 5#" ${coawstproj}/ocean.in 

#sed -i "s#WAV_name =.*#WAV_name = ${coawstproj}/swan.in#" ${coawstproj}/coupling.in
#sed -i "s#OCN_name =.*#OCN_name = ${coawstproj}/ocean.in#" ${coawstproj}/coupling.in

#sed -i "s#READGRID COORDINATES 1 .*#READGRID COORDINATES 1 '${coawstproj}/ann_coord.grd' 4 0 0 FREE#" ${coawstproj}/swan.in #change wave grid path
#sed -i "s#READINP BOTTOM  1.*#READINP BOTTOM 1 '${coawstproj}/ann_bathy.bot' 4 0 FREE#" ${coawstproj}/swan.in #change wave bathymetry path
#sed -i "s#COMPUTE NONSTATIONARY 20000101.000000 600 SEC.*# COMPUTE NONSTATIONARY 20000101.000000 600 SEC 20000101.120000#" ${coawstproj}/swan.in #change to 30 day run
#sed -i "s#NTIMES ==.*#NTIMES == 720#" ${coawstproj}/ocean.in #change simulation time
#sed -i "s#DT ==.*#DT == 5#" ${coawstproj}/ocean.in #change time step

#sed -i "s#GRDNAME ==.*#GRDNAME == ${coawstproj}/ann_grid.nc#" ${coawstproj}/ocean.in #change ROMS grid path
#sed -i "s#RSTNAME ==.*#RSTNAME == ${coawstproj}/ocean_rst.nc#" ${coawstproj}/ocean.in #replace restart file output location
#sed -i "s#HISNAME ==.*#HISNAME == ${coawstproj}/results/ocean_his.nc#" ${coawstproj}/ocean.in #replace history file output location
#sed -i "s#DIANAME ==.*#DIANAME == ${coawstproj}/results/ocean_dia.nc#" ${coawstproj}/ocean.in #replace diagnostics file output location 
#sed -i "s#AVGNAME ==.*#AVGNAME == ${coawstproj}/results/ocean_avg.nc#" ${coawstproj}/ocean.in #replace averages file output location

if [ ! -d "${coawstproj}/ocean_ini.nc" ]; then #create init file if doesn't exist
   cp ${coawstproj}/ocean_rip_current_rst.nc ${coawstproj}/ocean_ini.nc #copy restart file to init file
fi

#if [ ! -d "${coawstproj}/results" ]; then
#   mkdir ${coawstproj}/results
#fi

sed -i "s#NRREC ==.*#NRREC == -1#" ${coawstproj}/ocean.in #start new run initialized by restart
#sed -i "s#DSTART =.*#DSTART = 12.5d0                      !days#" ${coawstproj}/ocean.in #adjust start time
sed -i "s#ININAME ==.*# ININAME == ${coawstproj}/ocean_ini.nc#" ${coawstproj}/ocean.in #specify ini file
#sed -i "s#NDEFHIS ==.*#NDEFHIS == 0#" ${coawstproj}/ocean.in

#sed -i "s#MY_ROOT_DIR=.*#MY_ROOT_DIR=${MYGROUP}/COAWST#" ${coawstproj}/coawst.bash #change root before recompiling
#sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${coawstproj}#" ${coawstproj}/coawst.bash #change path before recompiling
#sed -i "s#VARNAME =.*#VARNAME = /group/pawsey0106/wtorres/COAWST/ROMS/External/varinfo.dat#" ${coawstproj}/ocean.in
sed -i "s#define ANA_INITIAL#undef ANA_INITIAL#" ${coawstproj}/rip_idealized.h

coawstcompile=$(sbatch --output=${coawstproj}/compile_rst.out --error=${coawstproj}/compile_rst.err --export=coawstproj=$coawstproj --parsable coawst_compile.slurm)

wait ${!}
sleep 1

sbatch --ntasks=$nprocs --ntasks-per-node=$taskspernode --nodes=$nodes \
--dependency=aftercorr:$coawstcompile \
--output=${coawstproj}/coawst_rst.out --error=${coawstproj}/coawst_rst.err --export=coawstproj=$coawstproj coawst_job.slurm


