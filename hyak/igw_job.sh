export suntansproj="/gscratch/nearshore/wtorres/opt/SUNTANS/examples/oblique_internal_wave" 

suntansgrid=$(sbatch --ntasks=20 --ntasks-per-node=20 --nodes=1 --output=${suntansproj}/grid.out --error=${suntansproj}/grid.err --export=suntansproj=$suntansproj --parsable suntans_grid.slurm)

wait ${!}
sleep 1

#sbatch --ntasks=$nprocs --ntasks-per-node=$taskspernode --nodes=$nodes \
#--dependency=aftercorr:$suntansgrid \
#--output=${suntansproj}/suntans.out --error=${suntansproj}/suntans.err --export=coawstproj=$coawstproj coawst_job.slurm

sbatch  --ntasks=20 --ntasks-per-node=20 --nodes=1 \
	--output=${suntansproj}/suntans.out --error=${suntansproj}/suntans.err \
	--export=suntansproj=$suntansproj \
	--dependency=aftercorr:$suntansgrid \
	suntans_job.slurm
