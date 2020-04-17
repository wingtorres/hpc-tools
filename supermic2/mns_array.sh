#!/bin/bash

cd /home/wtorres/COAWST
export mnsproj="/work/wtorres/MNS_Long"    
export homeproj="/home/wtorres/COAWST/Projects/MNS/Barotropic"

if [ ! -d "${mnsproj}" ]; then #create directory if doesn't exist
mkdir ${mnsproj}
mkdir ${mnsproj}/Results
cp -a Projects/MNS/Barotropic/. ${mnsproj} #copy all input/grid files to output folder
cp coawst_mns.bash ${mnsproj}
wait ${!}
fi

#Change analytic + header dir
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${mnsproj}#" ${mnsproj}/coawst_mns.bash

#Find and replace boundary conditions/input files and output path  

sed -i "s#RSTNAME ==.*#RSTNAME == ${mnsproj}/ocean_rst.nc#" ${mnsproj}/ocean_mns.in #replace restart file output location
sed -i "s#HISNAME ==.*#HISNAME == ${mnsproj}/Results/ocean_his_mns.nc#" ${mnsproj}/ocean_mns.in #replace history file output location
sed -i "s#DIANAME ==.*#DIANAME == ${mnsproj}/Results/ocean_dia_mns.nc#" ${mnsproj}/ocean_mns.in #replace diagnostics file output location 
sed -i "s#AVGNAME ==.*#AVGNAME == ${mnsproj}/Results/ocean_avg_mns.nc#" ${mnsproj}/ocean_mns.in #replace averages file output location
sed -i "s#FLTNAME ==.*#FLTNAME == ${mnsproj}/Results/ocean_flt_mns.nc#" ${mnsproj}/ocean_mns.in #replace floats file output location
sed -i -- "s#${homeproj}#${mnsproj}#g" ${mnsproj}/*.in #find and replace project file path in input files
sed -i -- "s#Projects/MNS/Barotropic#${mnsproj}#g" ${mnsproj}/*.in #find and replace project file path in input files


if [ ! -f "${mnsproj}/coawstM" ]; then #test if compilation successful
   mnscompile=$(qsub -v mnsproj mns_compile.pbs)
   qalter -o ${mnsproj}/${mnscompile}.compile.o -e ${mnsproj}/${mnscompile}.compile.e ${mnscompile}
   mnsjob=$(qsub -v mnsproj -W depend=afterok:$mnscompile mns_job.pbs)
   qalter -o ${mnsproj}/${mnsjob}.o -e ${mnsproj}/${mnsjob}.e ${mnsjob}
   wait ${!}
   sleep 1  
else #if already compiled run job
   mnsjob=$(qsub -v mnsproj)
   qalter -o ${mnsproj}/${mnsjob}.o -e ${mnsproj}/${mnsjob}.e ${mnsjob}
fi

