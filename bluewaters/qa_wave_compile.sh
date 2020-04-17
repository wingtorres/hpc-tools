#!/bin/bash
source ../coawst_config
module load nco
#cd COAWST

for i in {45,90} #loop through direction
do
for j in {45..45} #loop through latitude
do
dirname='qa_lat_'$(printf "%+.2d\n" $j)'_dir_'$(printf "%+.2d\n" $i) #name directory
echo "$dirname"

if [ ! -d "Output/$dirname" ]; then #create directory if doesn't exist
   mkdir Output/$dirname
   mkdir Output/${dirname}/Results
fi
   
   #change coriolis parameter (f) 
   ncap2 -s "where(f<1) f=2.0*0.0000729*sin($j*3.1415926535897932/180);" -O Projects/QA/Coupled/qa_grid.nc Projects/QA/Coupled/qa_grid.nc
#  ncks -v 'f' Projects/QA/Coupled/qa_grid.nc | more #how to view nc variable in text
   #make clean
   #./coawst_qa.bash > compile.txt & #compile
   #wait
   #cp coawstM Output/$dirname #move executable to output folder
   cp -a Projects/QA/Coupled/. Output/$dirname #copy all input/grid files to output folder
   sed -i "s#PAR [^ ]* [^ ]* [^ ]*#PAR 1.0 10.0 "$i"#g" Output/${dirname}/swan_qa.in #change wave direction
   sed -i "s#ocean_his_qa.nc#Output/${dirname}/Results/ocean_his_qa.nc#g" Output/${dirname}/ocean_qa.in #replace history file output location
   sed -i "s#ocean_dia_qa.nc#Output/${dirname}/Results/ocean_dia_qa.nc#g" Output/${dirname}/ocean_qa.in #replace diagnostics file output location 
   sed -i "s#ocean_avg_qa.nc#Output/${dirname}/Results/ocean_avg_qa.nc#g" Output/${dirname}/ocean_qa.in #replace averages file output location
   sed -i -- "s#Projects/QA/Coupled#Output/$dirname#g" Output/${dirname}/*.in #find and replace project file path in input files
done
done




