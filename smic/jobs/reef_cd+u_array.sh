#!/bin/bash
# Job submission loop for reef toy problem
#cd /home/wtorres/COAWST/Scripts

cppdef="REEF_IDEALIZED"
export homeproj="/home/wtorres/reef_idealized"
export ogproj="/Users/wit/COAWST/Projects/reef_idealized"
wavnodes=16
ocnnodes=144
export nprocs=$(($wavnodes + $ocnnodes))
export taskspernode=20
export nodes=$(($nprocs / $taskspernode))

dt=0.5 #time step
nt=518400 #total time of simulation in seconds
ntimes=$(echo "$nt/$dt" | bc)
nhis=$(echo "3600/$dt" | bc)
ndefhis=$(echo "86400/$dt" | bc)
navg=$(echo "300/$dt" | bc)
ndefavg=$(echo "3600/$dt" | bc)

#submission loop

#for rdrg2 in 0.007815 0.015625 0.03125 0.0625 0.125 0.25
#for rdrg2 in 0.25
#do
#for ubar in 0.0 0.01 0.02 0.04 0.08 0.16 
#for ubar in 0.02 0.04 0.08 
#do

rdrg2=0.125
ubar=0.16

#skip 15 day runs

if [ $rdrg2 = 0.03125 ] && [ $ubar = 0.02 ]; then 
   echo "skipping $rdrg2 $ubar"
   continue 
   continue
fi

if [ $rdrg2 = 0.03125 ] && [ $ubar = 0.04 ]; then 
   echo "skipping $rdrg2 $ubar"
   continue 
   continue
fi

if [ $rdrg2 = 0.03125 ] && [ $ubar = 0.005 ]; then 
   echo "skipping $rdrg2 $ubar"
   continue 
   continue
fi

dirname="cd_${rdrg2}_u_${ubar}"
export coawstproj="/work/wtorres/reef_idealized/${dirname}"

if [ ! -d "$coawstproj" ]; then #create directory if doesn't exist
   echo "creating ${coawstproj}"
   mkdir ${coawstproj}
   mkdir ${coawstproj}/output
else
   :
#   continue #if directory exists don't run code
fi
 
cp -au ${homeproj}/. ${coawstproj} #copy all input/grid files to output folder
wait ${!}

sed -i "s#RDRG2 ==.*#RDRG2 ==${rdrg2}d0#" ${coawstproj}/ocean.in
sed -i "s#q=.*#q=${ubar}_r8#" ${coawstproj}/ana_m2obc.h

sed -i "s#nodes=.*#nodes=${nodes}:ppn=${taskspernode}#" coawst_job.pbs
sed -i "s#NnodesWAV =.*#NnodesWAV = ${wavnodes}#" ${coawstproj}/coupling.in
sed -i "s#NnodesOCN =.*#NnodesOCN = ${ocnnodes}#" ${coawstproj}/coupling.in
sed -i "s#NtileI ==.*#NtileI == 18#" ${coawstproj}/ocean.in
sed -i "s#NtileJ ==.*#NtileJ == 8#" ${coawstproj}/ocean.in 

sed -i "s#WAV_name =.*#WAV_name = ${coawstproj}/swan.in#" ${coawstproj}/coupling.in
sed -i "s#OCN_name =.*#OCN_name = ${coawstproj}/ocean.in#" ${coawstproj}/coupling.in 

sed -i "s#DT ==.*#DT == ${dt}#" ${coawstproj}/ocean.in #change time step
sed -i "s#NTIMES ==.*#NTIMES == $ntimes#" ${coawstproj}/ocean.in #simulation duration
sed -i "s#NHIS ==.*#NHIS == $nhis#" ${coawstproj}/ocean.in #history output frequency
sed -i "s#NDEFHIS ==.*#NDEFHIS == $ndefhis#" ${coawstproj}/ocean.in #number time steps before new .nc file
sed -i "s#NAVG ==.*#NAVG == $navg#" ${coawstproj}/ocean.in #average output frequency
sed -i "s#NDEFAVG ==.*#NDEFAVG == $ndefavg#" ${coawstproj}/ocean.in
sed -i "s#NDIA ==.*#NDIA == $navg#" ${coawstproj}/ocean.in #diagnostic output frequency
sed -i "s#NDEFDIA ==.*#NDEFDIA == $ndefavg#" ${coawstproj}/ocean.in #number time steps before new .nc file

sed -i -- "s#${ogproj}#${coawstproj}#g" ${coawstproj}/*.in #find and replace project file path in input files

if [ ! -f "${coawstproj}/coawstM" ]; then #test if compilation successful

	cp /project/holstein/wtorres/COAWST/coawst.bash ${coawstproj}/coawst.bash #copy build script over
	sed -i "s#MY_PROJECT_DIR=.*#MY_PROJECT_DIR=${coawstproj}#" ${coawstproj}/coawst.bash #Change analytic + header dir
	sed -i "s#COAWST_APPLICATION=.*#COAWST_APPLICATION=${cppdef}#" ${coawstproj}/coawst.bash
	chmod +x ${coawstproj}/coawst.bash #fix permissions
	coawstcompile=$(qsub -e ${coawstproj}/compile.e -o ${coawstproj}/compile.o -v coawstproj coawst_compile.pbs)
	qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj,nprocs,taskspernode,nnodes -W depend=afterok:$coawstcompile coawst_job.pbs
	wait ${!}
	sleep 1

else
	 echo "already compiled"	
	 qsub -e ${coawstproj}/coawst.e -o ${coawstproj}/coawst.o -v coawstproj,nprocs,taskspernode,nodes coawst_job.pbs
fi

echo "^^^ submitted  ${coawstproj}"

#done
#done
