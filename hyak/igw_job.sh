export suntansproj="/gscratch/nearshore/wtorres/opt/SUNTANS/examples/oblique_internal_wave" 

### GRID & SUNTANS

# Grid build step

#suntansgrid=$(sbatch --ntasks=20 --ntasks-per-node=20 --nodes=1 --output=${suntansproj}/grid.out --error=${suntansproj}/grid.err --export=suntansproj=$suntansproj --parsable suntans_grid.slurm)

# Pause

wait ${!}
sleep 1

# Job submit

#sbatch  --ntasks=20 --ntasks-per-node=20 --nodes=1 \
#	--output=${suntansproj}/suntans.out --error=${suntansproj}/suntans.err \
#	--export=suntansproj=$suntansproj \
#	--dependency=aftercorr:$suntansgrid \
#	suntans_job.slurm


### SUNTANS only

sbatch  --ntasks=20 --ntasks-per-node=20 --nodes=1 \
        --output=${suntansproj}/suntans.out --error=${suntansproj}/suntans.err \
        --export=suntansproj=$suntansproj \
        suntans_job.slurm

