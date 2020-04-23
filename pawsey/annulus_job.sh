#!/bin/bash
#SBATCH --job-name="annulus"
#SBATCH --partition=workq
#SBATCH --time=24:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

cd $annproj
source ${MYGROUP}/coawst_modules
srun -n $SLURM_NTASKS ${annproj}/coawstM ${annproj}/coupling_ann.in
