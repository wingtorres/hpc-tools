module load nco

#take mean of three 2 hour long average records
ncra /scratch/eot/torres/slope_lat_+00_z0_0.25/Results/ocean_avg_ann_0016[678].nc /scratch/eot/torres/temp/full_avg6hr.nc
#resample diagnostic file 3hr to 6 hour by averaging every other index, and just use last index
ncks -d ocean_time,-2,,1 /scratch/eot/torres/slope_lat_+00_z0_0.25/Results/ocean_dia_ann_00014.nc /scratch/eot/torres/temp/temp.nc
ncra /scratch/eot/torres/temp/temp.nc /scratch/eot/torres/temp/full_dia6hr.nc  
#ncra -d ocean_time,-2,,2,2 --mro /scratch/eot/torres/slope_lat_-30_z0_0.25/Results/ocean_dia_ann_00014.nc /scratch/eot/torres/temp/full_dia6hr.nc 


