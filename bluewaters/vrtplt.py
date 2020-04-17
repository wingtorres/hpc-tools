#!/usr/bin/env python
import os
import sys
import netCDF4 as nc
import numpy as np
import subprocess
import csv

d = '/scratch/eot/torres/smol_lat_-20_kn_01/Results/' 
dir = os.listdir(d)
dir.sort()
vrt = np.empty(1)
time = np.empty(1)

for f in dir:
   if f.startswith('ocean_avg_ann'):
      print(f) 
   
   D = nc.Dataset(d+f)
   try: 
      vrt_add = np.sqrt(np.sum(np.array(D.variables['rvorticity'][:,:,:,:])**2, axis = (1,2,3) ))
      time_add = np.array(D.variables['ocean_time'][:])
      vrt = np.concatenate((vrt,vrt_add), axis = 0)
      time = np.concatenate((time,time_add), axis = 0)
   except:
       pass

datafile = "vrt.csv"
with open(datafile,"w") as f:
    writer = csv.writer(f,delimiter='\t')
    writer.writerows(('Time','vrt'))
    writer.writerows(zip(time[1:],vrt[1:]))

#pfile = "plot.p"
#with open(pfile,"w") as p:
#   lines = ["plot 

#subprocess.call['gnuplot']

 
