#!/bin/bash
#SBATCH --job-name="coawstM"
#SBATCH --output="coawst.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 6:00:00
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
./coawst_mns.bash -j
mpirun -np 192 ./coawstM Projects/MNS_rc20/DiffGrid/coupling_moorea_test_diffgrid.in
# mpirun -np 96 ./coawstM Projects/Stokes_test/DiffGrid/coupling_stokes_test_diffgrid.in
# mpirun -np 288 ./coawstM Projects/mns_benchmark/coupling_moorea_test_diffgrid.in
# mpirun -np 48 ./coawstM Projects/Stokes_test_quick/Refined/coupling_stokes_test_diffgrid.in
# mpirun -np 48 ./coawstM Projects/SI/Swanonly/swan_si.in
#mpirun -np 96 ./coawstM Projects/MNS_rc20/Swanonly/swan_moorea_test.in
# mpirun -np 96 ./coawstM Projects/Tetiaroa/DiffGrid/coupling_tetiaroa.in
