#!/bin/bash
# Job submission loop for reef toy problem
cd /home/wtorres/COAWST/Scripts

#for i in {0, 0.25, 5, 1, 2, 4, 8, 16} #currents: u (cm/s)
#for i in .25 16
#do
#for j in {.0625, .25, 1, 4, 16} #roughness length scale: z0 (cm)
#for j in .0625 16
#do
i=16
j=.0625

u=$(echo "$i/100" | bc -l)  #convert to m/s
ustr=$(printf "%0.6f\n" $u) 
z0=$(echo "$j/100" | bc -l) #convert to m
z0str=$(printf "%0.6f\n" $z0)
kN=$(echo "$j*30/100" | bc -l)
kNstr=$(printf "%0.6f\n" $kN)

dirname='reef_hs_075_u_'$(printf "%03g\n" $i)'_z0_'$(printf "%03g\n" $j) #name directory
export reefproj="/work/wtorres/${dirname}"
export homeproj="/home/wtorres/COAWST/Projects/reef"

   if [ ! -d "$reefproj" ]; then #create directory if doesn't exist
      mkdir ${reefproj}
      mkdir ${reefproj}/Results
      cp -a ${homeproj}/. ${reefproj} #copy all input/grid files to output folder
      wait ${!}
   fi

#Find and replace boundary conditions and output path 
sed -i "s#q = [^ ]*#q = "$ustr"_r8#" ${reefproj}/ana_m2obc.h
sed -i "s#q = [^ ]*#q = "$ustr"_r8#" ${reefproj}/ana_initial.h
sed -i "s#Zob == [^ ]\+#Zob == ${z0str}d0#" ${reefproj}/ocean_reef.in #z0
sed -i "s#FRICTION MADSEN .*#FRICTION MADSEN ${kNstr}#" ${reefproj}/swan_reef.in #kN

#sed -i "s#RESTART .*#RESTART ${reefproj}/swan_rst.dat#" ${reefproj}/swan_reef.in #replace wave restart file output location
#sed -i "s#RSTNAME == .*#RSTNAME == ${reefproj}/ocean_rst.nc#" ${reefproj}/ocean_reef.in #replace ocean restart file output location
#sed -i "s#HISNAME == .*#HISNAME == ${reefproj}/Results/ocean_his_reef.nc#" ${reefproj}/ocean_reef.in #replace history file output location
#sed -i "s#DIANAME == .*#DIANAME == ${reefproj}/Results/ocean_dia_reef.nc#" ${reefproj}/ocean_reef.in #replace diagnostics file output location 
#sed -i "s#AVGNAME == .*#AVGNAME == ${reefproj}/Results/ocean_avg_reef.nc#" ${reefproj}/ocean_reef.in #replace averages file output location
sed -i -- "s#${homeproj}#${reefproj}#g" ${reefproj}/*.in #find and replace project file path in input files

   if [ ! -f "${reefproj}/coawstM" ]; then #test if compilation successful
      cp /home/wtorres/COAWST/coawst_reef.bash ${reefproj} #copy build script over
      sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${reefproj}#" ${reefproj}/coawst_reef.bash #Change analytic + header dir
      chmod +x ${reefproj}/coawst_reef.bash #fix permissions
      reefcompile=$(qsub -e ${reefproj}/compile.e -o ${reefproj}/compile.o -v reefproj reef_compile.pbs)
      qsub -e ${reefproj}/reef.e -o ${reefproj}/reef.o -v reefproj -W depend=afterok:$reefcompile reef_job.pbs
      wait ${!}
      sleep 1
   else
      echo "already compiled"
      qsub -e ${reefproj}/reef.e -o ${reefproj}/reef.o -v reefproj reef_job.pbs
   fi

#done
#done
