#!/usr/bin/env python
import os
import sys
import netCDF4 as nc
import numpy as np
import subprocess
import csv

#Space index
i=1024
j=1

d = '/scratch/eot/torres/ann_lat_-30_kn_01/Results/' 
dir = os.listdir(d)
eta = np.empty(1)
time = np.empty(1)

for f in sorted(dir):
   if f.startswith('ocean_avg_ann') and float(f[-5:-3])>46:
      pass
   else:
      continue
  
   print(f) 
   
   D = nc.Dataset(d+f)
   eta_add = np.mean(np.array(D.variables['zeta'][:,j,:]),axis=1)
   time_add = np.array(D.variables['ocean_time'][:])
   
   eta = np.concatenate((eta,eta_add), axis = 0)
   time = np.concatenate((time,time_add), axis = 0)

datafile = "eta.csv"
with open(datafile,"w") as f:
    writer = csv.writer(f,delimiter='\t')
    writer.writerows(('Time','eta'))
    writer.writerows(zip(time[1:],eta[1:]))

#pfile = "plot.p"
#with open(pfile,"w") as p:
#   lines = ["plot 

#subprocess.call['gnuplot']

 
