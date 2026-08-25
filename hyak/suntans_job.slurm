#!/bin/bash

#SBATCH --job-name=suntans
#SBATCH --mail-type=END
#SBATCH --mail-user=wtorres@uw.edu	

#SBATCH --account=nearshore
#SBATCH --partition=compute
#SBATCH --time=02:00:00 # Max runtime in DD-HH:MM:SS format.

# Modules to use.
module load intel/oneAPI
export WORKDIR=/gscratch/nearshore/wtorres
source $WORKDIR/opt/suntans_config.sh 

echo "$SLURM_JOB_ID"
echo "$suntansproj"

#cd $WORKDIR/opt/SUNTANS/main
cd ${suntansproj}

#if changing boundary
make

# Your programs to run.
mpirun -np $SLURM_NTASKS ../../../main/sun -g --datadir=${suntansproj}
mpirun -np $SLURM_NTASKS ../../../main/sun -s -vv --datadir=${suntansproj}

