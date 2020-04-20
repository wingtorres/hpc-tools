#!/bin/bash
#SBATCH --job-name="annulus"
#SBATCH --partition=workq
#SBATCH --time=01:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

source ${MYGROUP}/coawst_modules
srun -n $SLURM_NTASKS ${annproj}/coawstM ${annproj}/coupling_ann.in
