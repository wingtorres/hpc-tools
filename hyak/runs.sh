#!/bin/bash

# load modules 
#module load matlab

# define useful functions and variables

vary_param () {
        #arguments
        #1 = suntansproj
        #2 = variable name (in suntans.dat)
        #3 = new value
        #4 = input file, if different than suntans.dat
        local inputfile="${4:-suntans.dat}"

        echo "Modifying '$2' to '$3' in $1/$inputfile..."
        #match variable name, preserve space, replace pattern with new value
        sed -i -E "s/^(${2}[[:space:]]+)[^[:space:]]+/\1$3/" "$1/$inputfile"
}

coriolis () {
        
	#Arguments
        local latitude=$1

        #Constants
	local omega="0.000072921159"
        
	#Coriolis parameter value (s^-1)
        local f=$( bc -l <<< "2 * $omega * s($latitude*(a(1)/45))")

        #Output
        echo "$f"
}

amp2vel () {
	
	#Arguments
	local amplitude=$1
	local depth=$2
       	local wavenumber=$(printf "%.12f" "$3")
    	local frequency=$(printf  "%.12f" "$4")	
	local coriolis=$(printf "%.12f" "$5")
	local pi=3.1415926535897932

	#Compute stratification
	#local N=$( bc -l <<< "$frequency/$wavenumber/$depth") local N2=$(bc -l <<< "$frequency^2*(  ($pi^2 + $wavenumber^2*$depth^2) - ($pi*$coriolis)^2 ) / ($wavenumber^2 * $depth^2)")
	local N2=$(bc -l <<< "($frequency^2 * ($pi^2 + $wavenumber^2*$depth^2) - ($pi*$coriolis)^2 ) / ($wavenumber^2 * $depth^2)")
		
	#echo "sqrt($N2)" | bc -l
	
	#output
	echo "$amplitude * sqrt($N2)" | bc -l
}

suntansproj="${WORKDIR}/opt/SUNTANS/examples/oblique_internal_wave"

# ==============================================================================

#for latitude in 0 45
#do
latitude=0

for A in 1 2 4 8 16
do

run="rundata_A_$A"
runpath="$suntansproj/$run"

# copy base project into new run directory, renamed

rsync -av "$suntansproj/data/"  "$runpath/"
cp "$suntansproj"/*.h "$runpath/"
cp "$suntansproj"/*.c "$runpath/"
cp "$suntansproj"/Makefile "$runpath/"

# Compute parameters to pass
f=$(coriolis "$latitude")

# fetch default params
input="$runpath/suntans.dat"
K=$(awk -v var="wavenumber" '$1==var {print $2}' $input)
omega=$(awk -v var="omega" '$1==var {print $2}' $input)
#H=(awk -v var="depth" '$1==var {print $2}' $input)
H=100

U=$(amp2vel "$A" "$H" "$K" "$omega" "$f")

# edit input files
vary_param "$runpath" "amp" "$U"
#vary_param "$runpath" "Coriolis_f" "$f"

#continue

# build grid, if necessary (MATLAB)
function_path="${suntansproj}/mfiles"
suntansfile="${runpath}/suntans.dat"
#matlab -batch "addpath('$function_path');  idealized_grid('$runpath', '$suntansfile')"

# submit job w/ enviromental parameters
#rundata=$runpath
#qsub -v rundata=$runpath suntans_run.pbs

sbatch  --ntasks=40 --ntasks-per-node=20 --nodes=2 \
        --output=${runpath}/suntans.out --error=${runpath}/suntans.err \
        --export=suntansproj=$runpath \
        suntans_job.slurm

wait
done

