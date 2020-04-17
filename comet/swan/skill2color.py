#!/opt/python/bin/python
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

#Parse output folders
namelist = [f for f in os.listdir('Output') if f.startswith('mns_alpha')]
l = 6 # # of stations
n = len(namelist) # # of model runs
skillmat = np.zeros((n,l+2));
for it in range(0,n):
    holdstr = namelist[it]
    skillmat[it,0] = holdstr[10:13]
    skillmat[it,1] = holdstr[20:24]
    skillmat[it,2:] = np.genfromtxt( open('Output/'+holdstr + '/mns_skill.txt',"rb") )

#Reshape skillmat for pcolor
alphaset = set(skillmat[:,0])
gammaset = set(skillmat[:,1])
alpha = [int(i) for i in alphaset]
gamma = [int(i) for i in gammaset]
alpha = np.asarray(alpha)
gamma = np.asarray(gamma)
#gamma = gamma/100
alpha = np.sort(alpha); # alpha = alpha[::-1]
gamma = np.sort(gamma); # gamma = gamma[::-1]
#print('%.2f' % gamma[0])
#alpha.sort()
#gamma.sort()
print('alpha  = ' + str(alpha))
print('gamma = ' + str(gamma))

alpha_ind = pd.factorize(skillmat[:,0] , sort = True)[0]
gamma_ind = pd.factorize(skillmat[:,1 ], sort = True)[0]

print(alpha_ind)
print(gamma_ind)

#print(skillmat)
statlist = [f for f in os.listdir('Output'+'/mns_bkd_alpha_100') if f.endswith('.table')] #station list
statlist.sort()
statlist = statlist[-1:] + statlist[:-1]
print(statlist)
[X,Y] = np.meshgrid(alpha,gamma)

print(X)
print(Y)
lowefig = plt.figure()
for pt in range(0,l): 
    cdata = np.zeros((len(gamma),len(alpha)) )
    for it in range(0,n):
        cdata[gamma_ind[it],alpha_ind[it]] = skillmat[it,pt+2]
    #print(cdata)
    plt.subplot(6,1,pt+1);
    plt.pcolor(X,Y,cdata, cmap = 'YlGnBu')
    plt.colorbar()
    pltname = statlist[pt]
    plt.title(pltname[0:3])
    plt.clim(.2,1)
    #if pt % 2 == 0:
    #    plt.ylabel('$ \\gamma $')
    #    plt.set_yticklabels([])
    if pt > 4:
        plt.xlabel('$ \\alpha $')
        
lowefig.tight_layout() 
#plt.show() 
lowefig.savefig('gamma_alpha.pdf', format='pdf')
#generate time series copmarison plot as well?/
