#!/bin/bash
#SBATCH --job-name="animate"
#SBATCH --partition=workq
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --time=00:30:00

conda activate viz
python ../visualisation/circ_animate.py $dirname
