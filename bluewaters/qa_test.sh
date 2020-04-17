#!/bin/bash
### set the number of nodes
### set the number of PEs per node
#PBS -l nodes=1:ppn=8:xe
### set the wallclock time
#PBS -l walltime=03:00:00
### set the job name
#PBS -N qa
### set the job stdout and stderr
#PBS -e $PBS_JOBID.err
#PBS -o $PBS_JOBID.out
### set email notification
##PBS -m torres
##PBS -M walter.torres@duke.edu
source coawst_config
module load nco
cd COAWST

for i in {5,10,20,30,-30} #loop through latitudes
do

dirname='qa_lat_'$(printf "%+.2d\n" $i) #name directory
echo "$dirname"

if [ ! -d "Output/$dirname" ]; then #create directory if doesn't exist
   mkdir Output/$dirname
fi
   #change coriolis parameter (f) 
   ncap2 -s "where(f<1) f=2.0*0.0000729*sin($i*3.1415926535897932/180);" -O Projects/QA/Coupled/qa_grid.nc Projects/QA/Coupled/qa_grid.nc
#   ncks -v 'f' Projects/QA/Coupled/qa_grid.nc | more #how to view nc variable in text
   ./coawst_qa.bash #compile
   cp coawstM Output/$dirname #move executable to output folder
   cp -a Projects/QA/Coupled/. Output/$dirname #copy all input/grid files to output folder
 
done




