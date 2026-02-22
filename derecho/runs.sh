#!/bin/bash

# load modules 
module load matlab

# define useful functions and variables

vary_param () {
        #arguments
        #1 = projectpath
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

projectpath="/glade/work/wtorres/idealized_siw/suntans-gvc-oblique-iw/examples/T_M1"

# ==============================================================================

for latitude in 0 45
do

#run="rundata_f_$latitude"
run="rundata"
runpath="$projectpath/$run"

# copy base project into new run directory, renamed

#rsync -av "$projectpath/rundata/"  "$runpath/"
#cp "$projectpath"/*.h "$runpath/"
#cp "$projectpath"/*.c "$runpath/"
#cp "$projectpath"/Makefile "$runpath/"

# Compute parameters to pass
f=$(coriolis "$latitude")

# edit input files
#vary_param "$runpath" "H" "$H"
vary_param "$runpath" "Coriolis_f" "$f"

# build grid, if necessary (MATLAB)
function_path="${projectpath}/mfiles"
suntansfile="${runpath}/suntans.dat"
#matlab -batch "addpath('$function_path');  idealized_grid('$runpath', '$suntansfile')"

# submit job w/ enviromental parameters
#rundata=$runpath
#qsub -v rundata=$runpath suntans_run.pbs

qsub suntans_run.pbs
wait
#break
done

