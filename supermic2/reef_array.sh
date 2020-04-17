#!/bin/bash
# Job submission loop for reef toy problem
cd /home/wtorres/COAWST
for i in {0,2,5} #,10,15,25,40} #currents (cm/s)
#for i in {0..40..40}
do
   for j in {210..240..30} #wave heights (cm)
   do
  
   #create directory name based on (u,hs)
   udir=$(echo "$i" | bc -l)
   udirstr=$(printf "%03g\n" $udir)
   hsdir=$(echo "$j" | bc -l)
   hsdirstr=$(printf "%03g\n" $hsdir)
   dirname='reef_u_'$udirstr'_hs_'$hsdirstr
   export reefproj="/work/wtorres/${dirname}"    
   export homeproj="/home/wtorres/COAWST/Projects/Reef/Coupled"
#   echo "$dirname"


   #convert to m/s and m for text replacement
   u=$(echo "$i/100" | bc -l)
   ustr=$(printf "%.2f\n" $u)
   hs=$(echo "$j/100" | bc -l)
   hsstr=$(printf "%.2f\n" $hs)
   
   if [ ! -d "${reefproj}" ]; then #create directory if doesn't exist
      mkdir ${reefproj}
      mkdir ${reefproj}/Results
      cp -a Projects/Reef/Coupled/. ${reefproj} #copy all input/grid files to output folder
      cp coawst_reef.bash ${reefproj}
      wait ${!}
   fi
   
   #Change analytic + header dir
   sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${reefproj}#" ${reefproj}/coawst_reef.bash
     
   #Find and replace boundary conditions and output path 
   sed -i "s/q = [^ ]*/q = "$ustr"_r8/" ${reefproj}/ana_m2obc.h
   sed -i "s/q = [^ ]*/q = "$ustr"_r8/" ${reefproj}/ana_initial.h
   sed -i "s/PAR [^ ]*/PAR "$hsstr"/" ${reefproj}/swan_reef.in
   sed -i "s#${homeproj}/ocean_rst.nc#${reefproj}/ocean_rst.nc#" ${reefproj}/ocean_reef.in #replace restart file output location
   sed -i "s#${homeproj}/ocean_his_reef.nc#${reefproj}/Results/ocean_his_reef.nc#" ${reefproj}/ocean_reef.in #replace history file output location
   sed -i "s#${homeproj}/ocean_dia_reef.nc#${reefproj}/Results/ocean_dia_reef.nc#" ${reefproj}/ocean_reef.in #replace diagnostics file output location 
   sed -i "s#${homeproj}/ocean_avg_reef.nc#${reefproj}/Results/ocean_avg_reef.nc#" ${reefproj}/ocean_reef.in #replace averages file output location
   sed -i "s#${homeproj}/ocean_flt_reef.nc#${reefproj}/Results/ocean_flt_reef.nc#" ${reefproj}/ocean_reef.in #replace floats file output location
   sed -i -- "s#${homeproj}#${reefproj}#g" ${reefproj}/*.in #find and replace project file path in input files
   
   if [ ! -f "${reefproj}/coawstM" ]; then #test if compilation successful
      reefcompile=$(qsub -v reefproj reef_compile.pbs)
      qsub -v reefproj -W depend=afterok:$reefcompile reef_job.pbs
      wait ${!}
      sleep 1  
   fi

   done
done
