#!/bin/bash
#SBATCH --job-name="compile"
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:30:00

source ${MYGROUP}/coawst_modules
/bin/bash ${annproj}/coawst_ann.bash -j

