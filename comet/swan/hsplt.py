import numpy as np
import os
#from os import listdir
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pandas import date_range
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FormatStrFormatter
import matplotlib.dates as dates
from scipy import io as sio

fdata = sio.loadmat('Projects/mns/moorea_north_shore_Jan2007_field_data_for_swan')

#Generate timestamps 
swantime =  date_range(start='1/12/2007 04:00:00', end = '1/15/2007 04:00:00', freq='H') #model time stamp
swantime = swantime[:-1] #trim last cell
fieldtime =  date_range(start='1/01/2007', periods = 744, freq='H') #field time stamp

indlow = fieldtime<=max(swantime)
indhigh = fieldtime>=min(swantime)
indgood = indlow*indhigh
t = fieldtime[indgood] #field timestamp. no need for interpolation

dname = 'Output/' #directory w/ model output
fname = 'hs_transect.png' #filename
r = [f for f in os.listdir(dname)]

#Plot H_s time series for each model run

for g in r:
    
    path = dname + g
    d = [f for f in os.listdir(path) if f.endswith('.table')] #find SWAN output
    d.sort()
    d = d[-1:] + d[:-1]
    hsfig = plt.figure()
    #print(path)
    #print(d) 
    for count,f in enumerate(d):
        holdstr = dname + '/' + g + '/' + f
        hs_o = fdata[f[0:3]+'_Hs']  #load field data
        hs_o = hs_o[indgood]
        hs_p = np.genfromtxt( open(holdstr,"rb"), delimiter=("      "), usecols = 0 , skip_header = 8) #fetch Hs
	hs_o = np.delete(hs_o,0) #clear first index
        plt.scatter(len(d)-count,np.nanmean(hs_p)) #plot Hs in loop
        #print(np.nanmean(hs_p))
        plt.scatter(len(d)-count,np.nanmean(hs_o),color = 'r')


    plt.ylabel('H_s (m)', color = 'w') 
    #hsfig.tick_params(axis='x',labelcolor='w')
    #hsfig.tick_params(axis='y',labelcolor='w')
    
    hsfig.savefig(fname, facecolor='w',format='png') #save figure
    os.rename(fname, dname + '/' + g +'/' + fname) #move file to directory
    print(g) #display

