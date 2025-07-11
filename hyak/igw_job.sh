export suntansproj="/gscratch/nearshore/wtorres/opt/SUNTANS/examples/oblique_internal_wave" 
sbatch --ntasks=40 --ntasks-per-node=20 --nodes=2 --output=${suntansproj}/suntans.out --error=${suntansproj}/suntans.err --export=suntansproj=$suntansproj suntans_job.slurm
