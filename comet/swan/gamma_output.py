#!/opt/python/bin/python
import numpy as np
import os
import glob
import shutil
import re
import fileinput, sys

#find alpha value and change it!
#regexp=re.compile(r'(?<=CON)(.*\d.*?)(ALPHA+)')
gamma = [];
with open('mns_parm.swn') as f:
	for line in f:
		match = re.search('(?<=GAMMA)(.*\d)',line)
		if match:
			gamma.append(match.group(1))

#print('Old gamma  = ' + gamma[0])
gamma_old = float(gamma[0]);
da = .1; #how much to change alpha by
gamma_new = gamma_old - da;
#print('New gamma = ' + str(gamma_new))
brkstr = 'BREAKING CON ALPHA 1.0 GAMMA ' + str(round(gamma_old,2)) 
print(brkstr)
newstr = 'BREAKING CON ALPHA 1.0 GAMMA ' + str(round(gamma_new,2));
print(newstr)
for line in fileinput.input('mns_parm.swn',inplace=1):
	line = re.sub(brkstr,newstr,line.rstrip())
	print(line)

#newest = max(glob.iglob('*.out'), key=os.path.getctime) #fetch most recent .out file
#dirname = newest[5:13]#folder name is run ID
dirname = 'mns_con_gamma_' + str(int(gamma_old*100)); 
source = os.listdir('/oasis/scratch/comet/wtorres/temp_project/SWAN');
if os.path.exists(dirname):
        shutil.rmtree(dirname) #delete folder in case it exists already
os.makedirs(dirname)   #create new folder for output
shutil.copy2('mns_parm.swn',dirname) #put input file into folder
for files in source:
        if files.endswith('.table'):
                shutil.copy2(files,dirname) #put station output into folder

test = 'Output/' + dirname
if os.path.exists(test):
        shutil.rmtree(test)
shutil.move(dirname,'Output/') #put model run in Output directory

###################################################

from scipy import io as sio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pandas import date_range
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FormatStrFormatter
import matplotlib.dates as dates

fdata = sio.loadmat('Projects/mns/moorea_north_shore_Jan2007_field_data_for_swan')
#sname = '/Users/WalterTorres/Dropbox/COAWST_Moorea/COMET_Matt/Swan_Only_Runs/10652523/'
#sname = '/Users/WalterTorres/Dropbox/Torres_French_Polynesia/Moorea_Island/BC_Wave/Output/swan_100517/'
#sname = '/Users/WalterTorres/Dropbox/Torres_French_Polynesia/Moorea_Island/BC_SWAN/'
sname = 'Output/' + dirname +'/'

#Generate timestamps 
swantime =  date_range(start='1/12/2007 04:00:00', end = '1/15/2007 04:00:00', freq='H') #model time stamp
swantime = swantime[:-1]; #trim last cell
fieldtime =  date_range(start='1/01/2007', periods = 744, freq='H') #field time stamp

indlow = fieldtime<=max(swantime);
indhigh = fieldtime>=min(swantime);
indgood = indlow*indhigh;
t = fieldtime[indgood]; #field timestamp. no need for interpolation

#Concatenate table namelist
brd = [f for f in os.listdir(sname) if f.startswith('br')]
brf = [f for f in os.listdir(sname) if f.startswith('fr')]
d = brf + brd;

njt = 5;
mns_skill = np.zeros((len(d),njt)); #preallocate skill
#for repeated time series data prealocate mns_skill a matrix..
#reshape data columns and iterate jt, use m rows on np.genfromtxt where m is # rows per numerical experiment
count = 0;
skillfig = plt.figure()
#fig, axes = plt.subplots(nrows=len(d), ncols=njt, sharex='col', sharey='row')
for jt in range(0,njt):
    for it in range(0,len(d)):
        count = count+1;
        holdstr = d[it] #fetch string from directory list
        hs_o = fdata[holdstr[0:3]+'_Hs'];  #load field data
        hs_o = hs_o[indgood];
        hs_p = np.genfromtxt( open(sname+holdstr,"rb"), delimiter=("      "), usecols = 0 , skip_header = 7+jt*hs_o.size, max_rows = (jt+1)*hs_o.size)
        hs_p = hs_p[range(0,len(swantime))];
        hs_o = np.delete(hs_o,0); #clear first index
        hs_p = np.delete(hs_p,0); #clear first index
        #load model data from table
        #mns_skill(it) = 1- ( np.nanmean( (hs_p-hs_o)**2 )**.5) ./ np.nanmean( (hs_o**2)**.5) )
        a = np.sum( (hs_p - hs_o)**2 );
        b = abs( hs_p - np.mean(hs_o));
        c = abs( hs_o - np.mean(hs_o));
        mns_skill[it,jt] = 1 - a/np.sum((b+c)**2);
        
        #fetch kn
        if holdstr in 'fr1.table':
            kn = np.genfromtxt( open(sname+holdstr,"rb"), delimiter=("      "), usecols = 3 , skip_header = 7+jt*hs_o.size, max_rows = (jt+1)*hs_o.size);
            knt = np.mean(kn);
            
        #Plotting
        
        sp = plt.subplot2grid( (len(d),njt) , (it,jt) );
 
        #plt.plot(swantime[1:],hs_o,'k' ) 
        #plt.plot(swantime[1:],hs_p,'r--') #modeled
        x = date_range(start='1/12/2007 04:00:00', end = '1/15/2007 03:00:00', freq='H'); x=x[1:];
        sp.plot_date(x.to_pydatetime(), hs_o,'k');   #observed
        sp.plot_date(x.to_pydatetime(), hs_p,'r--'); #modeled
        plt.ylim( (min(hs_o),max(hs_o)) );
        sp.xaxis.set_major_locator(dates.DayLocator())

        formatter = DateFormatter('%d')
        sp.xaxis.set_major_formatter(formatter)
        #p.xaxis.set_minor_formatter(dates.
        #plt.xticks(swantime[1:].to_pydatetime())
        #.locator_params(axis='x', nticks=4);
        sp.yaxis.tick_right()
        plt.text(0.85, 0.85,'IAS = ' + str( round(mns_skill[it,jt],2) ),
        horizontalalignment='center',
        verticalalignment='center',
        transform = sp.transAxes, fontsize = 6, color = 'blue')
        plt.grid()
        
        if jt == 0:
            plt.ylabel(holdstr[0:3])
            sp.set_yticklabels([])
        #else:if
            # = plt.subplot2grid( (len(d),njt) , (it,jt) , sharex = ax);
        if holdstr in 'fr1.table':
            sp.set_title('kN = ' + str(round(knt,2)),fontsize=10) 
        if jt != njt-1:
            sp.set_yticklabels([])
        else:
            plt.ylabel('H$_s$ (m)')
            sp.yaxis.set_label_position("right")
            sp.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        if it < len(d)-1:
            sp.set_xticklabels([])



skillfig.tight_layout()
# plt.show()

#Save file
np.savetxt('mns_skill',mns_skill)
skillfig.set_size_inches(11.0, 8.0)
skillfig.savefig('mns_skill.pdf', format='pdf')

#export results to output folder
shutil.copy2('mns_skill.pdf',test)
shutil.copy2('mns_skill',test)
