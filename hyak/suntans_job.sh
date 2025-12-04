### SUNTANS only

export suntansproj="/gscratch/nearshore/wtorres/opt/SUNTANS/examples/oblique_internal_wave"

sbatch  --ntasks=20 --ntasks-per-node=20 --nodes=1 \
        --output=${suntansproj}/suntans.out --error=${suntansproj}/suntans.err \
        --export=suntansproj=$suntansproj \
        suntans_job.slurm
