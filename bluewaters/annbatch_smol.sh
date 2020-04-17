#!/bin/bash
source /u/eot/torres/coawst_config
module load nco

for i in {0,-15,-30} #loop through latitude
do
for j in {.0625,.25,1,4,16} #loop through z0 (cm)
do
#i=-30
#j=.5

kN=$(echo "$j*30/100" | bc -l)
kNstr=$(printf "%0.6f\n" $kN)
z0=$(echo "$j/100" | bc -l)
z0str=$(printf "%0.6f\n" $z0)
d50=$(echo "$j*30/2.5/100" | bc -l)
d50str=$(printf "%0.6f\n" $d50)

dirname='smol_lat_'$(printf "%+03g\n" $i)'_z0_'$(printf "%03g\n" $j) #name directory
export annproj="/scratch/eot/torres/${dirname}"
export homeproj="/u/eot/torres/COAWST/Projects/Annulus/Smol"
#echo "$dirname"

if [ ! -d "$annproj" ]; then #create directory if doesn't exist
   mkdir ${annproj}
   mkdir ${annproj}/Results
   cp -a ${homeproj}/. ${annproj} #copy all input/grid files to output folder
   wait ${!}
fi

   #change coriolis parameter (f) 
   ncap2 -s "f=f*0+2.0*0.0000729*sin($i*3.1415926535897932/180);" -O ${homeproj}/ann_grid.nc ${annproj}/ann_grid.nc
   
   #https://stackoverflow.com/questions/148451/how-to-use-sed-to-replace-only-the-first-occurrence-in-a-file
   sed -i "0,/bottom(i,j,isd50)=.*/ s//bottom(i,j,isd50)=${d50str}_r8/" ${annproj}/ana_sediment.h #replace first match
   sed -i "s#Zob == [^ ]\+#Zob == ${z0str}d0#" ${annproj}/ocean_ann.in #z0
   sed -i "s#FRICTION MADSEN .*#FRICTION MADSEN ${kNstr}#" ${annproj}/swan_ann.in #kN
   sed -i "s#RSTNAME ==.*#RSTNAME == ${annproj}/ocean_rst.nc#" ${annproj}/ocean_ann.in #replace restart file output location
   sed -i "s#HISNAME ==.*#HISNAME == ${annproj}/Results/ocean_his_ann.nc#" ${annproj}/ocean_ann.in #replace history file output location
   sed -i "s#DIANAME ==.*#DIANAME == ${annproj}/Results/ocean_dia_ann.nc#" ${annproj}/ocean_ann.in #replace diagnostics file output location 
   sed -i "s#AVGNAME ==.*#AVGNAME == ${annproj}/Results/ocean_avg_ann.nc#" ${annproj}/ocean_ann.in #replace averages file output location
#   sed -i "s#${homeproj}/ocean_flt_ann.nc#${annproj}/Results/ocean_flt_ann.nc#" ${annproj}/ocean_ann.in #replace floats file output location
   sed -i -- "s#${homeproj}#${annproj}#g" ${annproj}/*.in #find and replace project file path in input files

   if [ ! -f "${annproj}/coawstM" ]; then #test if compilation successful
      cp /u/eot/torres/COAWST/coawst_ann.bash ${annproj} #copy build script over
      sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${annproj}#" ${annproj}/coawst_ann.bash #Change analytic + header dir
      chmod +x ${annproj}/coawst_ann.bash #fix permissions
      anncompile=$(qsub -e ${annproj}/compile.e -o ${annproj}/compile.o -v annproj ann_compile.pbs)
      qsub -e ${annproj}/ann.e -o ${annproj}/ann.o -v annproj -W depend=afterok:$anncompile smol_job.pbs
      wait ${!}
      sleep 1
   else
      #echo "hold"
      qsub -e ${annproj}/ann.e -o ${annproj}/ann.o -v annproj smol_job.pbs
   fi
#qsub -e ${annproj}/ann.e -o ${annproj}/ann.o -v annproj smol_job.pbs
done
done




