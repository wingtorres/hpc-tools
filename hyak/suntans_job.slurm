#!/bin/bash

#SBATCH --job-name=suntans
#SBATCH --mail-type=END
#SBATCH --mail-user=wtorres@uw.edu	

#SBATCH --account=nearshore
#SBATCH --partition=compute
#SBATCH --time=3:00:00 # Max runtime in DD-HH:MM:SS format.

# Modules to use.
module load intel/oneAPI
export WORKDIR=/gscratch/nearshore/wtorres
source $WORKDIR/opt/suntans_config.sh 

echo "$SLURM_JOB_ID"
echo "$suntansproj"

#cd $WORKDIR/opt/SUNTANS/main
cd ${suntansproj}

# Your programs to run.
#mpirun -np $SLURM_NTASKS ../../main/sun -t -g --datadir=${suntansproj}/rundata
mpirun -np $SLURM_NTASKS ../../main/sun -s -vv --datadir=${suntansproj}/rundata

