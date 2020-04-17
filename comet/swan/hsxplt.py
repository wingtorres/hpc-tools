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
#from scipy.interpolate import spline
from scipy.interpolate import pchip_interpolate as pchip
from scipy.interpolate import Akima1DInterpolator as akima

#plot Hs at stations for each parameterization.
#to make function... ???(srcpath,s74/gm/yu_***,gamma/alpha,val)

fdata = sio.loadmat('Projects/mns/moorea_north_shore_Jan2007_field_data_for_swan')

#Generate timestamps 
swantime =  date_range(start='1/12/2007 04:00:00', end = '1/15/2007 04:00:00', freq='H') #model time stamp
swantime = swantime[:-1] #trim last cell
fieldtime =  date_range(start='1/01/2007', periods = 744, freq='H') #field time stamp

indlow = fieldtime<=max(swantime)
indhigh = fieldtime>=min(swantime)
indgood = indlow*indhigh
t = fieldtime[indgood] #field timestamp. no need for interpolation

ro = [f for f in fdata if f.endswith('_Hs')] #find key names
ro.sort()
ro = ro[-1:] + ro[:-1]
obs = np.zeros((len(ro),1))

#Fetch field data from matlab dictionry
for it,f in enumerate(ro):
	#print(f)
	hs_o = fdata[f]
	hs_o = hs_o[indgood]
	hs_o = np.delete(hs_o,0) #clear first index 
	obs[it] = np.nanmean(hs_o)

#Fetch station positions
iname = 'stations.txt'
lon_i = np.genfromtxt(iname, delimiter = ' ', usecols = 0)
lat_i = np.genfromtxt(iname, delimiter = ' ', usecols = 1)
lon_i = np.delete(lon_i, [1,2] )
lat_i = np.delete(lat_i, [1,2])

dname = 'Output/plunge/' #directory w/ model output
if  'plunge' in dname:
	alph = '000'
elif 'roller' in dname:
	alph = '100'
pname = 'gm' #which friction paramterization
eorg = 'gamma' #holding which constant?
valu = '080'

#hsx(dname,pname,eorg,valu)

def hsx(src,param,alpha,var,val,obs):

	dname = src
	pname = param
	alph = alpha
	eorg = var
	valu = val

	estr = eorg #default...folders not named epsilon, so compensating to make code clear
	if eorg == 'knvar':
		estr = 'epsilon'

	fname = 'hsx_' + pname + '_' + 'alpha_' +  alph + '_'  + estr + '_' + valu + '.png' #filename
	#r = [f for f in os.listdir(dname) if f.endswith(pname) and eorg + '_' + valu in f]
	r = [f for f in os.listdir(dname) if f.startswith('mns_kn_') and eorg + '_' + valu in f]
	r.sort()
	#print(r)
	#Plot H_s time series for each model run on a figure
	ns = 6 # of stations to plot
	shold = np.zeros((ns,1))
	#ohold = shold
	xs = np.arange(ns,0,-1) #station #'s
	xp = np.linspace(lat_i.min(),lat_i.max(),500) #interpolate for plot
	#xp = xp[::-1] #reverse for plotting

	hsfig, ax = plt.subplots(nrows=1)
	
	Z = [[0,0],[0,0]]
	if estr == 'gamma':
	#	levels = range(0,400+25,25)
		levels = range(0,150+10,15)
	elif estr == 'epsilon':
		levels = range(20,200+20,20)
	CS3 = plt.contourf(Z, levels, cmap='Blues') #define colorbar then get rid of it
	plt.clf()
	for gcount,g in enumerate(r):
		    val = [int(s) for s in g.split('_') if s.isdigit()]
		    if estr == 'gamma':
			val =  float(val[0])
		    elif estr == 'epsilon':
			val = float(val[1])
		    #print(val)
		    print(g) 
		    path = dname + g
		    d = [f for f in os.listdir(path) if f.endswith('.table')] #find SWAN output
		    d.sort()
		    d = d[-1:] + d[:-1]
		    #d = d[1:]
		    #print(path)
		    #print(d) 
		    for count,f in enumerate(d):
			holdstr = dname + '/' + g + '/' + f
			hs_p = np.genfromtxt( open(holdstr,"rb"), delimiter=("      "), usecols = 0 , skip_header = 8) #fetch Hs
			shold[count] = np.nanmean(hs_p)
			#plt.scatter(len(d)-count,np.nanmean(hs_p),color = 'b',alpha = 1- val/400) #plot Hs in loop
			#print(np.nanmean(hs_p))
		    #yp = pchip(np.abs(lat_i),shold,np.abs(xp[::-1]))#,order = 3)
		    f_h = akima(np.abs(lat_i),shold)
		    yp = f_h(np.abs(xp[::-1]))
		    #print(shold)
		    #plt.plot(np.arange(6,0,-1),shold,color = plt.cm.Blues(1-val/400))
		    color = plt.cm.Blues(val/levels[-1])
		    plt.plot(xp,yp[::-1],color = color,zorder = 1)

	plt.scatter(lat_i,obs,s = 300, c = np.arange(obs.size) + 1, cmap = 'YlOrRd', marker = '*', edgecolor = 'k', linewidth = .5, vmin = 0, vmax = (obs.size+1)*2, zorder = 2) #plot field data
	if estr == 'gamma':
		cb = plt.colorbar(CS3,label = '$ \\epsilon $')
		cb.ax.set_ylabel('$ \\epsilon $',fontsize  = 24)
		#plt.title(pname + ' | '  '$ \\alpha = $' + alph + ' | ' '$ \\gamma = $' + valu)
	elif estr == 'epsilon':
		cb = plt.colorbar(CS3,label = '$ \\gamma $')
		cb.ax.set_ylabel('$ \\gamma $',fontsize = 24)
		#plt.title(pname + ' | '  '$ \\alpha = $' + alph + ' | ' '$  \\epsilon = $' + valu)

	fsz = 24 
	#plt.xlabel('Station',fontsize=fsz)
	plt.ylabel(r'$H_s$ (m)', fontsize=fsz) 
	plt.ylim(ymin = 0)
	#plt.xticks( np.arange(6)+1, [r'$\star$',r'$\star$',r'$\star$',r'$\star$',r'$\star$',r'$\star$'] )
	#plt.xlim( xmin = 1-.5, xmax = ns+.5 )
	#plt.tick_params(axis='x',labelsize = 24)
	plt.tick_params(axis='both',which='both',bottom ='off',top='off',left='off',right='off')
	ax = plt.gca()
	ax.axes.xaxis.set_ticklabels([])
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	#hsfig.tick_params(axis='x',labelcolor='w')
	#hsfig.tick_params(axis='y',labelcolor='w')    
	plt.tight_layout()
	hsfig.savefig(fname, facecolor='w',format='png', bbox_inches = 'tight') #save figure
	print('Figure saved as ' + fname)
	#os.rename(fname, dname + '/' + g +'/' + fname) #move file to directory
	#print(yp)
#Plotting time!
parlist = {}
srclist = {}
varlist = {}
#parlist["gm"] = ''
#parlist["yu_075"] = ''
#parlist["s74"] = ''
parlist["con"] = ''
srclist["Output/"] = '100'
#srclist["Output/alpha_100/"] = '100'
#srclist["Output/alpha_000/"] = '000'
varlist["gamma"] = '100'
#varlist["knvar"] = '250'

for s,alph in srclist.iteritems():
	for v,valu in varlist.iteritems():
		for p in parlist:
			hsx(s,p,alph,v,valu,obs)

#hsx(dname,pname,alph,eorg,valu,obs)

#test = plt.colormaps()
#print(test)

