#!/bin/bash
# Job submission loop for reef toy problem
module load matlab

cd /home/wtorres/COAWST


for i in {0..0..0} #,60} #,10,15,25,40} #sea level (cm)
do
   for j in {2,10} #z0 (cm)
   do
   
   kN=$(echo "$j*30/100" | bc -l)
   kNstr=$(printf "%0.2f\n" $kN)
   z0=$(echo "$j/100" | bc -l)
   z0str=$(printf "%0.2f\n" $z0)
   d50=$(echo "$j*30/2.5/100" | bc -l)
   d50str=$(printf "%0.2f\n" $d50)  
   
   dirname='reef_h0_'$(printf "%02g\n" $i)'_z0_'$(printf "%02g\n" $j)
   export reefproj="/work/wtorres/${dirname}"    
   export homeproj="/home/wtorres/COAWST/Projects/Reef/Coupled"

   if [ ! -d "${reefproj}" ]; then #create directory if doesn't exist
      mkdir ${reefproj}
      mkdir ${reefproj}/Results
      cp -a Projects/Reef/Coupled/. ${reefproj} #copy all input/grid files to output folder
      cp coawst_reef.bash ${reefproj}
      wait ${!}
   fi
   
   #Change analytic + header dir
   sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${reefproj}#" ${reefproj}/coawst_reef.bash

   #change depth
#   ncap2 -s "h=h+$i/100;" -O ${homeproj}/reef_grid.nc ${reefproj}/reef_grid.nc
   matlab -nodisplay -nodesktop -nosplash -nojvm -r "changeBathy ${homeproj}/reef_grid.nc ${reefproj}/reef_grid.nc $i; exit"   
   mv swan_bathy.bot reef_bathy.bot #rename matlab output from roms2swan
   cp reef_bathy.bot ${reefproj}/reef_bathy.bot #replace bathy file in folder

   #Find and replace boundary conditions/input files and output path  
   sed -i "s#bottom(i,j,isd50)=0.12_r8#bottom(i,j,isd50)=${d50str}_r8#" ${reefproj}/ana_sediment.h #d50 
   sed -i "s#Zob == [^ ]\+#Zob == ${z0str}d0#" ${reefproj}/ocean_reef.in #z0
   sed -i "s#FRICTION MADSEN [^ ]*#FRICTION MADSEN ${kNstr}#" ${reefproj}/swan_reef.in #kN
   sed -i "s#${homeproj}/ocean_rst.nc#${reefproj}/ocean_rst.nc#" ${reefproj}/ocean_reef.in #replace restart file output location
   sed -i "s#${homeproj}/ocean_his_reef.nc#${reefproj}/Results/ocean_his_reef.nc#" ${reefproj}/ocean_reef.in #replace history file output location
   sed -i "s#${homeproj}/ocean_dia_reef.nc#${reefproj}/Results/ocean_dia_reef.nc#" ${reefproj}/ocean_reef.in #replace diagnostics file output location 
   sed -i "s#${homeproj}/ocean_avg_reef.nc#${reefproj}/Results/ocean_avg_reef.nc#" ${reefproj}/ocean_reef.in #replace averages file output location
   sed -i "s#${homeproj}/ocean_flt_reef.nc#${reefproj}/Results/ocean_flt_reef.nc#" ${reefproj}/ocean_reef.in #replace floats file output location
   sed -i -- "s#${homeproj}#${reefproj}#g" ${reefproj}/*.in #find and replace project file path in input files
   
   if [ ! -f "${reefproj}/coawstM" ]; then #test if compilation successful
      reefcompile=$(qsub -v reefproj reef_compile.pbs)
      qalter -o ${reefproj}/${reefcompile}.compile.o -e ${reefproj}/${reefcompile}.compile.e ${reefcompile}
      reefjob=$(qsub -v reefproj -W depend=afterok:$reefcompile reef_job.pbs)
      qalter -o ${reefproj}/${reefjob}.o -e ${reefproj}/${reefjob}.e ${reefjob}
      wait ${!}
      sleep 1  
   fi

   done
done
