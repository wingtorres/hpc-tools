#!/opt/python/bin/python
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

#Parse output folders
namelist = [f for f in os.listdir('Output/') if f.startswith('mns_kn_')]
l = 6 # # of stations
n = len(namelist) # # of model runs
skillmat = np.zeros((n,l+2));
for it in range(0,n):
    holdstr = namelist[it]
    skillmat[it,0] = holdstr[7:10]
    skillmat[it,1] = holdstr[17:21]
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

print(kn_ind)
print(gamma_ind)

#print(skillmat)
statlist = [f for f in os.listdir('Output'+'/mns_bkd_alpha_100') if f.endswith('.table')] #station list
statlist.sort()
statlist = statlist[-1:] + statlist[:-1]
print(statlist)
[X,Y] = np.meshgrid(kn,gamma)

print(X)
print(Y)
agg_skill = np.zeros((len(gamma),len(kn)))
lowefig = plt.figure()
count = 0
for pt in [1,2,3,5]: 
    count = count+1
    cdata = np.zeros((len(gamma),len(kn)) )
    for it in range(0,n):
        cdata[gamma_ind[it],kn_ind[it]] = skillmat[it,pt+2]
    #print(cdata)
    ax = lowefig.add_subplot(4,1,count)
    p = plt.pcolor(X,Y,cdata, cmap = 'YlGnBu_r')
    #cbar = plt.colorbar(p,use_gridspec=True)
    #cbar.ax.set_yticklabels([])
    #cbar.ax.yaxis.set_tick_params(labelcolor='w')
    pltname = statlist[pt]
    plt.title(pltname[0:3],color = 'white')
    plt.clim(.2,1)
    #if pt % 2 == 0:
    plt.ylabel('$ \\gamma $',color='white')
    #plt.set_yticklabels([])
    ax.tick_params(axis='x',labelcolor='w')
    ax.tick_params(axis='y',labelcolor='w')
    agg_skill += cdata
    if pt == 5:
        plt.xlabel('kN (cm)',color='white')
    else:
        ax.set_xticklabels([])
lowefig.tight_layout() 
#plt.show() 
lowefig.savefig('gamma_kn.png', facecolor='k', format='png')
#lowefig.savefig('gamma_kn.png', format='png')
#generate time series copmarison plot as well?/
#print(agg_skill/4)

fsz = 20
aggfig, ax  = plt.subplots()
plt.pcolor(X,Y,agg_skill/4,cmap='RdPu')
plt.ylabel( '$ \\gamma $',fontsize = fsz)
plt.xlabel('$k_{N}$ (cm)', fontsize = fsz)
plt.xlim( (X.min(),X.max()) )
plt.clim( (.3,.9) )
ticks = ax.get_yticks()/100
ax.set_yticklabels(ticks)
#plt.title('Aggregate Skill')
cb = plt.colorbar()
#cb.make_axes(location = 'top')
cb.ax.get_yaxis().labelpad=15
aggfig.savefig('kngam_agg.png',format = 'png',bbox_inches = 'tight')

