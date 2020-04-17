#!/bin/bash
#SBATCH --job-name="coawstM"
#SBATCH --output="island.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 06:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

#This job runs ith 1 node, x cores per node for a total of y cores.
#ibrun in verbose mode will give binding detail

MODULEPATH=$MODULEPATH:/share/apps/compute/modulefiles/applications
module purge
module load gnutools
module load intel/2016.3.210
module load intelmpi
module load netcdf/4.3.2intelmpi
#./coawst_stokes.bash -j 96
mpirun -np 96 ./coawstM Projects/island/Coupled/coupling_ii.in
