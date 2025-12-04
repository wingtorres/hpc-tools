#!/bin/bash

#SBATCH --job-name=coawst
#SBATCH --mail-type=END
#SBATCH --mail-user=wtorres@uw.edu	

#SBATCH --account=nearshore
#SBATCH --partition=compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=40
#SBATCH --time=24:00:00 # Max runtime in DD-HH:MM:SS format.

#SBATCH --chdir=/gscratch/nearshore/wtorres/opt/COAWST
##SBATCH --output=${coawstproj}/coawst.out # where STDOUT goes
##SBATCH --error=${coawstproj}/coawst.err  # where STDERR goes

# Modules to use.
module load intel/oneAPI
export WORKDIR=/gscratch/nearshore/wtorres
source $WORKDIR/opt/coawst_vars.sh 

echo "$SLURM_JOB_ID"
echo "$LD_LIBRARY_PATH"
echo "${coawstproj}/coupling.in"

cd /gscratch/nearshore/wtorres/opt/COAWST

# Your programs to run.
mpirun -np $SLURM_NTASKS ${coawstproj}/coawstM ${coawstproj}/coupling.in
