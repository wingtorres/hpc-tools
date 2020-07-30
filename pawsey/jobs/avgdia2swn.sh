#!/bin/bash
#SBATCH --job-name="avgdia2swnm"
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --time=02:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

cd ${MYGROUP}/COAWST/hpc-tools/pawsey/visualisation
echo "$SLURM_JOB_ID"
source activate viz
python avgdia2swnm_interp.py 
echo "done"
