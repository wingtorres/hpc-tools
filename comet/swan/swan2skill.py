#!/opt/python/bin/python
import numpy as np
from os import listdir
from scipy import io as sio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pandas import date_range
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FormatStrFormatter
import matplotlib.dates as dates

fdata = sio.loadmat('Projects/mns/moorea_north_shore_Jan2007_field_data_for_swan')

#Generate timestamps 
swantime =  date_range(start='1/12/2007 04:00:00', end = '1/15/2007 04:00:00', freq='H') #model time stamp
swantime = swantime[:-1] #trim last cell
fieldtime =  date_range(start='1/01/2007', periods = 744, freq='H') #field time stamp

indlow = fieldtime<=max(swantime)
indhigh = fieldtime>=min(swantime)
indgood = indlow*indhigh
t = fieldtime[indgood] #field timestamp. no need for interpolation

#Concatenate table namelist
d = [f for f in listdir('.') if f.endswith('.table')]
d.sort()
d = d[-1:] + d[:-1]
mns_skill = np.zeros(len(d)) #preallocate skill
#for repeated time series data prealocate mns_skill a matrix..
#reshape data columns and iterate jt, use m rows on np.genfromtxt where m is # rows per numerical experiment
count = 0
skillfig = plt.figure()
#fig, axes = plt.subplots(nrows=len(d), ncols=njt, sharex='col', sharey='row')
#for it in range(0,len()):
for it in [0,1,2,3,4,5]:
  count = count+1
  holdstr = d[it] #fetch string from directory list
  hs_o = fdata[holdstr[0:3]+'_Hs']  #load field data
  hs_o = hs_o[indgood]
  hs_p = np.genfromtxt( open(holdstr,"rb"), delimiter=("      "), usecols = 0 , skip_header = 7 , max_rows = hs_o.size)
  hs_p = hs_p[range(0,len(swantime))]
  hs_o = np.delete(hs_o,0) #clear first index
  hs_p = np.delete(hs_p,0) #clear first index
  
  #skill calculation
  a = np.sum( (hs_p - hs_o)**2 )
  b = abs( hs_p - np.mean(hs_o))
  c = abs( hs_o - np.mean(hs_o))
  mns_skill[it] = 1 - a/np.sum((b+c)**2)
        
  #Plotting      
  #sp = plt.subplot2grid( (len(d),1) , (it,1) )
  sp = plt.subplot(3,2,count)
  x = date_range(start='1/12/2007 05:00:00', end = '1/15/2007 03:00:00', freq='H')
  sp.plot_date(x.to_pydatetime(), hs_o,'k')   #observed
  sp.plot_date(x.to_pydatetime(), hs_p,'r--') #modeled
  #plt.ylim( (min(hs_o),max(hs_o)) )
  plt.title(holdstr[0:3],color='white')
  sp.xaxis.set_major_locator(dates.DayLocator())

  formatter = DateFormatter('%d')
  sp.xaxis.set_major_formatter(formatter)
  #sp.yaxis.tick_right()
  plt.text(0.90, 0.15,'IAS = ' + str( round(mns_skill[it],2) ),
  horizontalalignment='center',
  verticalalignment='center',
  transform = sp.transAxes, fontsize = 12, color = 'blue')
  #plt.grid()
  
  sp.tick_params(axis='x',labelcolor='w')
  sp.tick_params(axis='y',labelcolor='w')
  if it == 0:
     plt.legend(['Observed','Modeled'],loc="upper left",frameon=False)
  
  if count > 3:
     plt.xlabel('Days',color='white')
  else:
     sp.axes.get_xaxis().set_ticks([])

skillfig.tight_layout()

#Save file
np.savetxt('mns_skill.txt',mns_skill)
skillfig.set_size_inches(11.0, 8.0)
#skillfig.savefig('mns_skill.pdf', format='pdf')
skillfig.savefig('mns_skill.png', facecolor='k',format='png')

