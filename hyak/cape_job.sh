export coawstproj="/gscratch/nearshore/wtorres/opt/COAWST/Projects/cape_idealized"

#coawstcompile=$(sbatch --output=${coawstproj}/compile.out --error=${coawstproj}/compile.err --export=coawstproj=$coawstproj --parsable coawst_compile.slurm)

#wait ${!}
#sleep 1

#	--dependency=aftercorr:$coawstcompile \

sbatch --ntasks=40 --ntasks-per-node=40 --nodes=1 \
	--output=${coawstproj}/coawst.out --error=${coawstproj}/coawst.err --export=coawstproj=$coawstproj \
	coawst_job.slurm

