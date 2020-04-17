#!/bin/bash
source /u/eot/torres/coawst_config
module load nco
#cd COAWST

for i in {0,-30} #loop through latitude
do
for j in {1,10} #loop through z0 (cm)
do
#i=0
#j=1

kN=$(echo "$j*30/100" | bc -l)
kNstr=$(printf "%0.2f\n" $kN)
z0=$(echo "$j/100" | bc -l)
z0str=$(printf "%0.2f\n" $z0)
d50=$(echo "$j*30/2.5/100" | bc -l)
d50str=$(printf "%0.2f\n" $d50)

dirname='ann_lat_'$(printf "%+03d\n" $i)'_kn_'$(printf "%02g\n" $j) #name directory
export annproj="/scratch/eot/torres/${dirname}"
#export homeproj="Projects/Annulus/Barotropic"
export homeproj="/u/eot/torres/COAWST/Projects/Annulus/Barotropic"
#echo "$dirname"

if [ ! -d "$annproj" ]; then #create directory if doesn't exist
   mkdir ${annproj}
   mkdir ${annproj}/Results
   cp -a ${homeproj}/. ${annproj} #copy all input/grid files to output folder
   cp coawst_ann.bash ${annproj}
   wait ${!}
fi

   #Change analytic + header dir
   sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${annproj}#" ${annproj}/coawst_ann.bash
   
   #change coriolis parameter (f) 
   #ncap2 -s "where(f<1) f=2.0*0.0000729*sin($i*3.1415926535897932/180);" -O ${homeproj}/ann_grid.nc ${annproj}/ann_grid.nc
   ncap2 -s "f=f*0+2.0*0.0000729*sin($i*3.1415926535897932/180);" -O ${homeproj}/ann_grid.nc ${annproj}/ann_grid.nc
   
   sed -i "s#bottom(i,j,isd50)=0.3_r8#bottom(i,j,isd50)=${d50str}_r8#" ${annproj}/ana_sediment.h #d50 
   sed -i "s#Zob == [^ ]\+#Zob == ${z0str}d0#" ${annproj}/ocean_ann.in #z0
   sed -i "s#FRICTION MADSEN [^ ]*#FRICTION MADSEN ${kNstr}#" ${annproj}/swan_ann.in #kN
   sed -i "s#ocean_rst.nc#${annproj}/ocean_rst.nc#" ${annproj}/ocean_ann.in #replace restart file output location
   sed -i "s#ocean_his_ann.nc#${annproj}/Results/ocean_his_ann.nc#" ${annproj}/ocean_ann.in #replace history file output location
   sed -i "s#ocean_dia_ann.nc#${annproj}/Results/ocean_dia_ann.nc#" ${annproj}/ocean_ann.in #replace diagnostics file output location 
   sed -i "s#ocean_avg_ann.nc#${annproj}/Results/ocean_avg_ann.nc#" ${annproj}/ocean_ann.in #replace averages file output location
#   sed -i "s#${homeproj}/ocean_flt_ann.nc#${annproj}/Results/ocean_flt_ann.nc#" ${annproj}/ocean_ann.in #replace floats file output location
   sed -i -- "s#${homeproj}#${annproj}#g" ${annproj}/*.in #find and replace project file path in input files

   if [ ! -f "${annproj}/coawstM" ]; then #test if compilation successful
      anncompile=$(qsub -e ${annproj}/compile.e -o ${annproj}/compile.o -v annproj ann_compile.pbs)
      #qalter -o ${annproj}/${anncompile}.compile.o -e ${annproj}/${anncompile}.compile.e ${anncompile}
      qsub -e ${annproj}/ann.e -o ${annproj}/ann.o -v annproj -W depend=afterok:$anncompile annulus_job.pbs
      #qalter -o ${annproj}/${annjob}.o -e ${annproj}/${annjob}.e ${annjob} 
      wait ${!}
      sleep 1
   fi

done
done




