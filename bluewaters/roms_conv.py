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

def pcinit(ax,x,y,z,title):
    
    #pc.set_array(z[:-1,:-1].ravel()) 
    pc = ax.pcolormesh(x,y,z, vmin = -.25, vmax = .25, cmap = 'RdBu_r')
    ax.set_title(title,color = 'w')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_aspect('equal')
    
    #Dark mode 
    ax.set_facecolor('k')
    ax.spines['left'].set_color('w')
    ax.spines['bottom'].set_color('w')    
    #ax.xaxis.label.set_color('w')
    #ax.yaxis.label.set_color('w')
    ax.tick_params(axis='x', colors= 'w')
    ax.tick_params(axis='y', colors= 'w')
    return pc 

def roms_plot(filename,imdest,lon,lat,lon_u,lat_u,lon_v,lat_v):

    A = nc.Dataset(filename)
    t = np.array(A.variables['ocean_time'][:])
    u_e = np.array(A.variables['u'][:,-1,:,:])
    v_e = np.array(A.variables['v'][:,-1,:,:])
    u_s = np.array(A.variables['u_stokes'][:,-1,:,:])
    v_s = np.array(A.variables['v_stokes'][:,-1,:,:])
    u = np.squeeze(u_e + u_s)
    v = np.squeeze(v_e + v_s)
    
    F,(ax1,ax2) = plt.subplots(1,2,facecolor = 'k')
    pcu = pcinit(ax1, lon_u, lat_u, lon_u*0, 'u')
    pcv = pcinit(ax2, lon_v, lat_v, lon_v*0, 'v')
    plt.tight_layout()
    #pcu = ax1.pcolormesh(lon_u,lat_u,lon_u*0, vmin = -.25, vmax = .25, cmap = 'RdBu_r')
    #pcv = ax2.pcolormesh(lon_v,lat_v,lon_v*0, vmin = -.25, vmax = .25, cmap = 'RdBu_r')
    for k,t in enumerate(t[::2]):

        ind = ((t+150)/300 + 1)/2
        up = np.squeeze(u[k,:,:])
        vp = np.squeeze(v[k,:,:])
        pcu.set_array(up[:-1,:-1].ravel())
        pcv.set_array(vp[:-1,:-1].ravel())
        #pcdark(ax1, pcu, lon_u, lat_u, np.squeeze((u[k,:,:]),'u')
        #pcdark(ax2, pcv, lon_v, lat_v, np.squeeze(v[k,:,:]),'v') 
        #plt.tight_layout()
        F.savefig(imdest+"ann_{:04}.png".format(int(ind)), dpi=100, facecolor='k', edgecolor = 'none')
    
    plt.close(F)

for f in D:
    print(f)
    filename = dirpath+f
    roms_plot(filename,imdest,lon,lat,lon_u,lat_u,lon_v,lat_v)
           
