#!/bin/bash
#SBATCH -A dku126
#SBATCH --job-name="SWAN"
#SBATCH --output="swan.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=10
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 12:00:00
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

for i in {1..15}
do
  for j in {1..10}
  do

  #Edit and replace kn/gamma values then run SWAN
  kn=$(echo "$i*.1" | bc)
  knstr=$(printf "%03f\n" $kn)
  gamma=$(echo "$j*.2" | bc)
  gammastr=$(printf "%03f\n" $gamma)  
  echo "kN = $knstr"
  echo "Gamma = $gammastr"
  sed -i "s/MADSEN [^ ]*/MADSEN "$knstr"/" mns_test.swn
  sed -i "s/GAMMA [^ ]*/GAMMA "$gammastr"/" mns_test.swn
  ./swanrun -input mns_test -mpi 240

  #Create directory name from kn/gamma values
  kndir=$(echo "$kn*100" | bc )  
  kndirstr=$(printf "%03g\n" $kndir)
  gammadir=$(echo "$gamma*100" | bc)
  gammadirstr=$(printf "%03g\n" $gammadir)
  dirname='mns_kn_'$kndirstr'_gamma_'$gammadirstr
  echo "$dirname"
  
  #Create folder & move model output
  rm -rf Output/$dirname; mkdir Output/$dirname
   python swan2skill.py
   mv *.table Output/$dirname
   cp mns_test.swn Output/$dirname 
   mv mns_skill* Output/$dirname
  
  done
done


#./swanrun -input mns
#mpirun -np 24 ./mns.swn
#mpirun_rsh -hostfile $SLURM_NODEFILE -np 24 . mns.swn
