#!/bin/bash
projdir=${MYSCRATCH}/bluewaters

for f in "$projdir"/*
do


export annproj=$f
echo "$f"

#sed -i "0,/bottom(i,j,isd50)=.*/ s//bottom(i,j,isd50)=${d50str}_r8/" ${annproj}/ana_sediment.h #d50 replace first match 
#sed -i "s#Zob == [^ ]\+#Zob == 0.01d0#" ${annproj}/ocean_ann.in #z0
#sed -i "s#FRICTION MADSEN [^ ]*#FRICTION MADSEN 0.3#" ${annproj}/swan_ann.in #kN
#sed -i "/Restart name \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/a RESTART ${annproj}/swan_rst.dat FREE 3 HR" ${annproj}/swan_ann.in
#sed -i '0,/RESTART.*/ s///' ${annproj}/swan_ann.in

#mv -v ${annproj}/results/ocean_his_ann_00027.nc ${annproj}/results/ocean_his_ann_00014.nc
#mv -v ${annproj}/results/ocean_dia_ann_00027.nc ${annproj}/results/ocean_dia_ann_00014.nc
mv -v ${annproj}/results/ocean_his_dia_00014.nc ${annproj}/results/ocean_dia_ann_00014.nc 

#sed -i "/PROP BSBT/a INIT HOTSTART MULTIPLE '${annproj}/swan_rst.dat' " ${annproj}/swan_ann.in
#cp coawstM ${annproj}/


done




