#!/bin/bash

cd /home/wtorres/COAWST
export tetproj="/work/wtorres/tetiaroa-coarse"    
export homeproj="Projects/Tetiaroa/Barotropic"

if [ ! -d "${tetproj}" ]; then #create directory if doesn't exist
mkdir ${tetproj}
mkdir ${tetproj}/Results
cp -a ${homeproj}/. ${tetproj} #copy all input/grid files to output folder
cp coawst_tet.bash ${tetproj}
wait ${!}
fi

#Change analytic + header dir
sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${tetproj}#" ${tetproj}/coawst_tet.bash

#Find and replace boundary conditions/input files and output path  

sed -i "s#RSTNAME ==.*#RSTNAME == ${tetproj}/ocean_rst.nc#" ${tetproj}/ocean_tetiaroa.in #replace restart file output location
sed -i "s#HISNAME ==.*#HISNAME == ${tetproj}/Results/ocean_his_tet.nc#" ${tetproj}/ocean_tetiaroa.in #replace history file output location
sed -i "s#DIANAME ==.*#DIANAME == ${tetproj}/Results/ocean_dia_tet.nc#" ${tetproj}/ocean_tetiaroa.in #replace diagnostics file output location 
sed -i "s#AVGNAME ==.*#AVGNAME == ${tetproj}/Results/ocean_avg_tet.nc#" ${tetproj}/ocean_tetiaroa.in #replace averages file output location
sed -i "s#FLTNAME ==.*#FLTNAME == ${tetproj}/Results/ocean_flt_tet.nc#" ${tetproj}/ocean_tetiaroa.in #replace floats file output location
sed -i -- "s#${homeproj}#${tetproj}#g" ${tetproj}/*.in #find and replace project file path in input files


if [ ! -f "${tetproj}/coawstM" ]; then #test if compilation successful
   tetcompile=$(qsub -v tetproj tet_compile.pbs)
   qalter -o ${tetproj}/${tetcompile}.compile.o -e ${tetproj}/${tetcompile}.compile.e ${tetcompile}
   tetjob=$(qsub -v tetproj -W depend=afterok:$tetcompile tet_job.pbs)
   qalter -o ${tetproj}/${tetjob}.o -e ${tetproj}/${tetjob}.e ${tetjob}
   wait ${!}
   sleep 1  
else #if already compiled run job
   tetjob=$(qsub -v tetproj)
   qalter -o ${tetproj}/${tetjob}.o -e ${tetproj}/${tetjob}.e ${tetjob}
fi

