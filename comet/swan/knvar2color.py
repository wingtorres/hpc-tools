#!/opt/python/bin/python
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

#Parse output folders
#parselist = [f for f in os.listdir('Output') if f.startswith('mns_knvar') and not f.endswith('_*')]
#namelist = [f for f in parselist if len(f)<24]

#aggfig = plt.subplots(1,3)
aggfig = plt.subplots(1,3,figsize=(7.5,10))
for fc,ff in enumerate(['gm','s74','yu_075']):
	aggname = 'knvargam_agg_' + ff + '.png'
	namelist = [f for f in os.listdir('Output') if f.endswith(ff)]
	print(namelist)
	l = 6 # # of stations
	n = len(namelist) # # of model runs
	skillmat = np.zeros((n,l+2));
	for it in range(0,n):
	    holdstr = namelist[it]
	    skillmat[it,0] = holdstr[10:13]
	    skillmat[it,1] = holdstr[20:23]
	    skillmat[it,2:] = np.genfromtxt( open('Output/'+holdstr + '/mns_skill.txt',"rb") )

	#Reshape skillmat for pcolor
	knset = set(skillmat[:,0])
	gammaset = set(skillmat[:,1])
	kn = [int(i) for i in knset]
	gamma = [int(i) for i in gammaset]
	kn = np.asarray(kn)
	gamma = np.asarray(gamma)
	#gamma = gamma/100
	kn = np.sort(kn); # alpha = alpha[::-1]
	gamma = np.sort(gamma); # gamma = gamma[::-1]
	#print('%.2f' % gamma[0])
	#kn.sort()
	#gamma.sort()
	print('kn  = ' + str(kn))
	print('gamma = ' + str(gamma))

	kn_ind = pd.factorize(skillmat[:,0] , sort = True)[0]
	gamma_ind = pd.factorize(skillmat[:,1 ], sort = True)[0]

	#Aggregate skill vs. kn/gam

	#print(kn_ind)
	#print(gamma_ind)
	#print(skillmat)
	statlist = [f for f in os.listdir('Output'+'/mns_bkd_alpha_100') if f.endswith('.table')] #station list
	statlist.sort()
	statlist = statlist[-1:] + statlist[:-1]
	print(statlist)
	[X,Y] = np.meshgrid(kn,gamma)

	agg_skill = np.zeros((len(gamma),len(kn)))
#	lowefig = plt.figure()
#	count = 0
	for pt in [1,2,3,5]: 
#	    count = count+1
	    cdata = np.zeros((len(gamma),len(kn)) )
	    for it in range(0,n):
		cdata[gamma_ind[it],kn_ind[it]] = skillmat[it,pt+2]
#	    #print(cdata)
#	    ax = lowefig.add_subplot(3,2,count)
#	    p = plt.pcolor(X,Y,cdata, cmap = 'YlGnBu_r')
#	    plt.colorbar()
#	    #cbar = plt.colorbar(p,use_gridspec=True)
#	    #cbar.ax.set_yticklabels([])
#	    #cbar.ax.yaxis.set_tick_params(labelcolor='w')
#	    pltname = statlist[pt]
#	    plt.title(pltname[0:3],color = 'k')
#	    plt.clim(.2,1)
#	    #if pt % 2 == 0:
#	    #plt.ylabel('$ \\gamma $',color='k')
#	    #plt.set_yticklabels([])
#	    ax.tick_params(axis='x',labelcolor='k')
#	    ax.tick_params(axis='y',labelcolor='k')
	    agg_skill += cdata
#	    if pt % 2 == 0:
#		plt.ylabel('$ \\gamma $',color='k')
#	    if pt > 3:
#		plt.xlabel('$ \\epsilon $',color='k')
#	    else:
#		ax.set_xticklabels([])
#	#lowefig.tight_layout() 
#	#lowefig.savefig('knvar_gam.png', facecolor='w', format='png')


	fsz = 18
	ax  = plt.subplot(1,3,fc+1)
	#ax.set_aspect('equal','datalim')
	ax.pcolor(X,Y,agg_skill/4,cmap = 'RdPu',vmin = .3, vmax = .9)
	ax.set_xlim( (X.min(),X.max()) )	
	ax.set_aspect(aspect=2,adjustable='box')
	#ax.set_aspect('equal','datalim')
	if fc == 0:
		ax.set_ylabel( '$ \\gamma $',fontsize = fsz)
	ax.set_xlabel('$ \\epsilon $',fontsize = fsz)
	plt.title(ff)
	#plt.title('Aggregate Skill')
	#cb = plt.colorbar() 
	#cb.ax.get_yaxis().labelpad=15
	#cb.ax.set_ylabel('Skill',rotation =270,fontsize = 18)
	#ax.set_clim(vmin = .3,vmax = .9)
#	plt.axis('equal')
	ticks = ax.get_yticks()/100
	ax.set_yticklabels(ticks)
	for label in ax.yaxis.get_ticklabels()[::2]:
		label.set_visible(False)
	ticks = ax.get_xticks()/100
	ax.set_xticklabels(ticks)
	for label in ax.xaxis.get_ticklabels()[::2]:
    		label.set_visible(False)
	ax.tick_params(axis='both',labelsize=8)
	#aggfig.tight_layout()
	#aggfig.savefig(aggname,format = 'png',bbox_inches = 'tight')

	#print(np.matrix(agg_skill/4))
	#print('Figure saved as ' + aggname)
	#np.savetxt('gamma_gm.txt',Y)
	#np.savetxt('knvar_gm.txt',X)
	#np.savetxt('skill_yu.txt',agg_skill/4)
plt.tight_layout()
#aggfig.tight_layout()
plt.savefig('knvargam_agg.png',format = 'png',bbox_inches = 'tight')
