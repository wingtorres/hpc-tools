#!/bin/bash
#SBATCH --job-name="compile"
#SBATCH --partition=compute
#SBATCH --account=nearshore
#SBATCH --dependency=singleton
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:30:00
#SBATCH --chdir=/gscratch/nearshore/wtorres/opt/COAWST

module load intel/oneAPI
module load cmake/3.21.1  
export WORKDIR=/gscratch/nearshore/wtorres
source ${WORKDIR}/opt/coawst_vars.sh

#source ~/.bashrc
#conda activate coawst
#source $WORKDIR/coawst-conda/config

cd /gscratch/nearshore/wtorres/opt/COAWST

/bin/bash ${coawstproj}/build_coawst.sh -j


