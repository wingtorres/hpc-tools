#!/bin/bash
#SBATCH --job-name="SWAN"
#SBATCH --output="swan.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=10
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 06:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

MODULEPATH=$MODULEPATH:/share/apps/compute/modulefiles/applications
module purge
module load gnutools
#module load intel/2016.3.210
module load intel/2013_sp1.2.144
module load intelmpi
#module load netcdf/4.3.2intelmpi
module load python
module load scipy
export PATH=${PATH}:/oasis/scratch/comet/wtorres/temp_project/SWAN/./
#./swanrun -input mns_parm -mpi 240

for i in {1..7}
do
  for j in {1..6}
  do

  #Edit and replace kn/gamma values then run SWAN
  kn=$(echo "$i*.5+.5" | bc)
  knstr=$(printf "%.2f\n" $kn)
  gamma=$(echo "$j*.1+.3" | bc)
  gammastr=$(printf "%.1f\n" $gamma)  
  echo "kN = $knstr"
  echo "Gamma = $gammastr"
  sed -i "s/READINP FRIC [^ ]*/READINP FRIC "$knstr"/" mns_knvar.swn
  sed -i "s/GAMMA [^ ]*/GAMMA "$gammastr"/" mns_knvar.swn
  ./swanrun -input mns_knvar -mpi 240

  #Create directory name from kn/gamma values
  kndir=$(echo "$i*50+50" | bc )
  kndirstr=$(printf "%03g\n" $kndir)
  gammadir=$(echo "$j*10+30" | bc)
  gammadirstr=$(printf "%03g\n" $gammadir)
  dirname='mns_knvar_'$kndirstr'_gamma_'$gammadirstr'_s74'
  echo "$dirname"
  
  #Create folder & move model output
  rm -rf Output/$dirname; mkdir Output/$dirname
   python swan2skill.py
   mv *.table Output/$dirname
   cp mns_knvar.swn Output/$dirname 
   mv mns_skill* Output/$dirname
  
  done
done


#./swanrun -input mns
#mpirun -np 24 ./mns.swn
#mpirun_rsh -hostfile $SLURM_NODEFILE -np 24 . mns.swn
