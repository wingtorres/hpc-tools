#!/bin/bash
# Job submission loop for reef toy problem
#cd /home/wtorres/COAWST/Scripts

dirname="annulus_thermal-test"
export coawstproj="/work/wtorres/${dirname}"
export homeproj="/home/wtorres/COAWST/Projects/analytic"

if [ ! -d "$coawstproj" ]; then #create directory if doesn't exist
   mkdir ${coawstproj}
   mkdir ${coawstproj}/Results
fi
 
cp -au ${homeproj}/. ${coawstproj} #copy all input/grid files to output folder
wait ${!}

hs=0.5
python spec_mod.py ${coawstproj}/spec.bnd $hs  #edit file
mv spec_temp.txt ${coawstproj}/spec.bnd #overwrite file

wavnodes=16
ocnnodes=144
nprocs=$(($wavnodes + $ocnnodes))
taskspernode=20
nodes=$(($nprocs / $taskspernode))

sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${coawstproj}/coupling.in
sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${coawstproj}/coupling.in
sed -i "s#NtileI ==.*#NtileI == 24#" ${coawstproj}/ocean.in
sed -i "s#NtileJ ==.*#NtileJ == 6#" ${coawstproj}/ocean.in 


dt=1 #time step
nt=86400 #total time of simulation in seconds
sed -i "s#DT ==.*#DT == ${dt}#" ${coawstproj}/ocean.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $((nt / dt))#" ${coawstproj}/ocean.in #simulation duration
sed -i "s#NHIS ==.*#NHIS == $((3600 / dt))#" ${coawstproj}/ocean.in #history output frequency
sed -i "s#NDEFHIS ==.*#NDEFHIS == $((3600 / dt))#" ${coawstproj}/ocean.in #number time steps before new .nc file
sed -i "s#NDIA ==.*#NDIA == $((600 / dt))#" ${coawstproj}/ocean.in #diagnostic output frequency
sed -i "s#NDEFDIA ==.*#NDEFDIA == $((3600 / dt))#" ${coawstproj}/ocean.in #number time steps before new .nc file
sed -i "s#NAVG ==.*#NAVG == $((600 / dt))#" ${coawstproj}/ocean.in #average output frequency
sed -i "s#NDEFAVG ==.*#NDEFAVG == $((3600 / dt))#" ${coawstproj}/ocean.in

sed -i -- "s#${homeproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files

#return

   if [ ! -f "${coawstproj}/coawstM" ]; then #test if compilation successful
      cp /home/wtorres/COAWST/coawst_ann.bash ${coawstproj} #copy build script over
      sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${coawstproj}#" ${coawstproj}/coawst_ann.bash #Change analytic + header dir
      chmod +x ${coawstproj}/coawst_ann.bash #fix permissions
      coawstcompile=$(qsub -e ${coawstproj}/compile.e -o ${coawstproj}/compile.o -v coawstproj coawst_compile.pbs)
      qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj, nprocs, taskspernode, nodes -W depend=afterok:$coawstcompile coawst_job.pbs
      wait ${!}
      sleep 1
   else
      echo "already compiled"
      qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj,nprocs,taskspernode,nodes coawst_job.pbs
   fi

