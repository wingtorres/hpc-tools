#!/bin/bash
#Job submission script for SWAN runs

jid=$(sbatch swan_job.sh)

for value in {0..1..3}
do
  pid=$(sbatch --dependency=afterany:$jid py_job.sh)
  jid=$(sbatch --dependency=afterany:$pid swan_job.sh)
done
