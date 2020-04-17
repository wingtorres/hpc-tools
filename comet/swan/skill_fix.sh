#!/bin/bash
#SBATCH --job-name="skill"
#SBATCH --output="skill.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=5
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 00:10:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

MODULEPATH=$MODULEPATH:/share/apps/compute/modulefiles/applications
module purge
module load gnutools
#module load intel/2016.3.210
module load intel/2013_sp1.2.144
#module load intelmpi
#module load netcdf/4.3.2intelmpi
module load python
module load scipy
#export PATH=${PATH}:/oasis/scratch/comet/wtorres/temp_project/SWAN/./
#./swanrun -input mns_parm -mpi 240

for i in {1..6}
do
  for j in {1..9}
  do

  #Edit and replace alpha/gamma values then run SWAN
  alpha=$(echo "$i*.2-.2" | bc)
  alphastr=$(printf "%.1f\n" $alpha)
  gamma=$(echo "$j*.1+.6" | bc)
  gammastr=$(printf "%.1f\n" $gamma)  
  echo "Alpha = $alphastr"
  echo "Gamma = $gammastr"
  sed -i "s/ALPHA [^ ]*/ALPHA "$alphastr"/" mns_test.swn
  sed -i "s/GAMMA [^ ]*/GAMMA "$gammastr"/" mns_test.swn
  # ./swanrun -input mns_test -mpi 240

  #Create directory name from alpha/gamma values
  alphadir=$(echo "$i*20-20" | bc )
  alphadirstr=$(printf "%03g\n" $alphadir)
  gammadir=$(echo "$j*10+60" | bc)
  gammadirstr=$(printf "%03g\n" $gammadir)
  dirname='mns_alpha_'$alphadirstr'_gamma_'$gammadirstr
  echo "$dirname"
  
  #Pull model output out then replace mns_skill
  #rm -rf Output/$dirname; mkdir Output/$dirname
  cp Output/$dirname/*.table .
  python swan2skill.py
  mv mns_skill.txt Output/$dirname
  
  done
done


#./swanrun -input mns
#mpirun -np 24 ./mns.swn
#mpirun_rsh -hostfile $SLURM_NODEFILE -np 24 . mns.swn
