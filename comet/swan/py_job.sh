#!/bin/bash
#SBATCH --job-name="python"
#SBATCH --output="python.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --export=ALL
#SBATCH -t 00:00:10
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

#This job runs ith 1 node, x cores per node for a total of y cores.
#ibrun in verbose mode will give binding detail

MODULEPATH=$MODULEPATH:/share/apps/compute/modulefiles/applications
module purge
module load intel/2016.3.210
module load python
module load scipy
python gamma_output.py
#python beta_output.py
