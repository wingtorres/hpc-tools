#!/bin/bash
# Job submission loop for reef toy problem
#cd /home/wtorres/COAWST/Scripts

cppdef="SLOPE"
export homeproj="/home/wtorres/COAWST/Projects/slope_2D"

lat=30

for rdrg2 in 0.0
do
for slope in 0.0
do
for vbar in 0.5
do

dirname="cd_${rdrg2}_slope_${slope}_vbar_${vbar}"
export coawstproj="/work/wtorres/slope_2D_runs/${dirname}"

if [ ! -d "$coawstproj" ]; then #create directory if doesn't exist
   mkdir ${coawstproj}
   mkdir ${coawstproj}/Results
fi
 
cp -au ${homeproj}/. ${coawstproj} #copy all input/grid files to output folder
wait ${!}

wavnodes=0
ocnnodes=40
export nprocs=$(($wavnodes + $ocnnodes))
export taskspernode=20
export nodes=$(($nprocs / $taskspernode))
 
sed -i "s#nodes=.*#nodes=${nodes}:ppn=${taskspernode}#" roms_job.pbs

#sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${coawstproj}/coupling.in
#sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${coawstproj}/coupling.in
sed -i "s#NtileI ==.*#NtileI == 10#" ${coawstproj}/ocean.in
sed -i "s#NtileJ ==.*#NtileJ == 4#" ${coawstproj}/ocean.in 

#PBS -l nodes=${nnodes}:ppn=${taskspernode}

dt=0.25 #time step
nt=7200 #total time of simulation in seconds
ntimes=$(echo "$nt/$dt" | bc)
nhis=$(echo "3600/$dt" | bc)
ndefhis=$(echo "43200/$dt" | bc)
navg=$(echo "300/$dt" | bc)
ndefavg=$(echo "3600/$dt" | bc)

sed -i "s#DT ==.*#DT == ${dt}#" ${coawstproj}/ocean.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $ntimes#" ${coawstproj}/ocean.in #simulation duration
sed -i "s#NHIS ==.*#NHIS == $nhis#" ${coawstproj}/ocean.in #history output frequency
sed -i "s#NDEFHIS ==.*#NDEFHIS == $ndefhis#" ${coawstproj}/ocean.in #number time steps before new .nc file
sed -i "s#NAVG ==.*#NAVG == $navg#" ${coawstproj}/ocean.in #average output frequency
sed -i "s#NDEFAVG ==.*#NDEFAVG == $ndefavg#" ${coawstproj}/ocean.in
sed -i "s#NDIA ==.*#NDIA == $navg#" ${coawstproj}/ocean.in #diagnostic output frequency
sed -i "s#NDEFDIA ==.*#NDEFDIA == $ndefavg#" ${coawstproj}/ocean.in #number time steps before new .nc file

sed -i -- "s#${homeproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files

   if [ ! -f "${coawstproj}/coawstM" ]; then #test if compilation successful
      cp /home/wtorres/COAWST/coawst.bash ${coawstproj} #copy build script over
      sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${coawstproj}#" ${coawstproj}/coawst.bash #Change analytic + header dir
      sed -i "s#COAWST_APPLICATION=.*#COAWST_APPLICATION=${cppdef}#" ${coawstproj}/coawst.bash
      chmod +x ${coawstproj}/coawst.bash #fix permissions
      coawstcompile=$(qsub -e ${coawstproj}/compile.e -o ${coawstproj}/compile.o -v coawstproj coawst_compile.pbs)
      qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj,nprocs,taskspernode,nnodes -W depend=afterok:$coawstcompile roms_job.pbs
      wait ${!}
      sleep 1
   else
      echo "already compiled"
      qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj,nprocs,taskspernode,nodes roms_job.pbs
   fi
done
done
done
