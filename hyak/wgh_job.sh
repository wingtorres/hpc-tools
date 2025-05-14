export coawstproj="/gscratch/nearshore/wtorres/opt/COAWST/Projects/wgh" 
sbatch --ntasks=80 --ntasks-per-node=40 --nodes=2 --output=${coawstproj}/coawst.out --error=${coawstproj}/coawst.err --export=coawstproj=$coawstproj coawst_job.slurm
