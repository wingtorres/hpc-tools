#!/bin/bash
#SBATCH --job-name="SWAN"
#SBATCH --output="swan.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=18
#SBATCH --export=ALL
#SBATCH -t 02:00:00
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
./swanrun -input si -mpi 18

