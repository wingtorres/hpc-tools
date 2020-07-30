#!/bin/bash
directories=/scratch/pawsey0106/wtorres/doneski/*
#filepaths = sorted([directory + f + '/results/' for f in os.listdir(directory) ])

for f in $directories
do

#sbatch --export=dirname=${f} animate_pyjob.sh
echo $f

done

