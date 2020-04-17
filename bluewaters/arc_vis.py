#!/usr/bin/env python

#import parsl
#import os
#from parsl.app.app import python_app, bash_app
#from config.bluewaters import config
#import sys
#sys.exit()

import os
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck

gridname = '/scratch/eot/torres/smol_lat_-20_kn_01/ann_grid.nc'
dirpath = '/scratch/eot/torres/smol_lat_-20_kn_01/Results/'
imdest = '/scratch/eot/torres/vis/'
D = [d for d in os.listdir(dirpath) if d.startswith("ocean_avg_ann")];
D.sort()

#Grid Variables
G = nc.Dataset(gridname)
lon = np.array(G.variables['x_rho'][:,:])/1e3
lat = np.array(G.variables['y_rho'][:,:])/1e3
lon_u = np.array(G.variables['x_u'][:,:])/1e3
lat_u = np.array(G.variables['y_u'][:,:])/1e3
lon_v = np.array(G.variables['x_v'][:,:])/1e3
lat_v = np.array(G.variables['y_v'][:,:])/1e3

t = np.squeeze(np.arctan2(lat[0,:],lon[0,:]))
t = (t[1:]+t[0:-1])/2

def axinit(ax,title):
    
    #pc.set_array(z[:-1,:-1].ravel()) 
    #lp = ax.plot(r,r*0,'w.')
    ax.set_title(title,color = 'w')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    #Dark mode 
    ax.set_facecolor('k')
    ax.spines['left'].set_color('w')
    ax.spines['bottom'].set_color('w')    
    #ax.xaxis.label.set_color('w')
    #ax.yaxis.label.set_color('w')
    ax.tick_params(axis='x', colors= 'w')
    ax.tick_params(axis='y', colors= 'w')
    return

def roms_plot(filename): #,imdest,ax,lon,lat,lon_u,lat_u,lon_v,lat_v):

    A = nc.Dataset(filename)
    time = np.array(A.variables['ocean_time'][:])
    vrt = np.squeeze(np.array(A.variables['rvorticity'][:,-1,79:,:]))
    #u_e = np.array(A.variables['u'][:,-1,:,:])
    #v_e = np.array(A.variables['v'][:,-1,:,:])
    #u_s = np.array(A.variables['u_stokes'][:,-1,:,:])
    #v_s = np.array(A.variables['v_stokes'][:,-1,:,:])
    #u = np.squeeze(u_e + u_s)
    #v = np.squeeze(v_e + v_s)
    
    #pcv = ax2.pcolormesh(lon_v,lat_v,lon_v*0, vmin = -.25, vmax = .25, cmap = 'RdBu_r')
    #var = np.squeeze(np.mean(vrt**2,axis = 1))
    dy = abs(np.diff(lat[80:,:],axis=1))*1e3
    var = np.trapz( abs(vrt**2)*dy, x = lon[80:,0]*1e3, axis = 1)
    
    #ax.plot(t,vrt_var.T,'w-',linewidth = .1)
    #F.savefig(imdest+"ann_{:04}.png".format(int(ind)), dpi=100, facecolor='k', edgecolor = 'none')
    #plt.close(F)
    return var, time

plt.style.use("dark_background")
F,ax = plt.subplots(1,facecolor = 'k')
axinit(ax,"$(\mathcal{E}')$")
ax.set_xlabel('Days')
ax.set_ylabel(r'$\theta$')
#ax.yaxis.set_major_formatter(tck.FuncFormatter(
#   lambda val,pos: '{:.0g}$\pi$'.format(val/np.pi) if val !=0 else '0'
#))
#ax.yaxis.set_major_locator(tck.MultipleLocator(base=np.pi/12))


var = np.empty( (0,len(t)) ) 
time = np.empty(0)
for f in D:
    print(f)
    filename = dirpath+f
    var_add, time_add = roms_plot(filename) #,lon,lat,lon_u,lat_u,lon_v,lat_v)
    #print(var.shape, var_add.shape)
    var = np.concatenate( (var,var_add), axis = 0)
    time = np.concatenate( (time,time_add) )

T, Time = np.meshgrid(t,time)

dev = var - np.tile( var.mean(axis=0), (len(time),1) )
pc = ax.pcolormesh(Time/3600/24, T, abs(dev), cmap = 'magma', vmin = 0, vmax =.1)
cb = F.colorbar(pc, ax = ax)
cb.set_label(r'$\frac{m^2}{s^2}$', color = 'w')
#cb.ax.yaxis.set_tick_params(color='w')
#cb.outline.set_edgecolor('w')

plt.tight_layout()
F.savefig("/u/eot/torres/COAWST/Scripts/varplt.pdf", facecolor = 'k', edgecolor = None)
plt.close(F)
