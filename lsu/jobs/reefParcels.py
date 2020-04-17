import sys
import xarray as xr
import numpy as np
from datetime import timedelta as delta
from parcels import AdvectionRK4, ErrorCode, FieldSet, JITParticle, ParticleFile, ParticleSet

#filename = home + '/Desktop/anntest_strided2D.nc'
#filestack = '/Users/WalterTorres/Dropbox/COAWST_Moorea/Stokes_Toy/runs_z0/reef_hs_100_z0_.0025_u_.16-logdrag-m94/Results/ocean_avg_reef*'
filenames =  "/work/wtorres/particles/*nc"
Ds = xr.open_mfdataset(filenames, chunks={'ocean_time': 12}, combine="by_coords", parallel=True, decode_times = False)
#print(Ds)
#sys.exit()

x = Ds['x_psi'].values
y = Ds['y_psi'].values
t = Ds['ocean_time'].values
#w = Ds['w']#*Ds['mask_rho']

#velocity to psi points
u_eulerian = 0.5*( Ds['u'].isel(eta_u = slice(0,-1)) + Ds['u'].isel(eta_u = slice(1,None)) ).rename({'xi_u': 'xi_psi', 'eta_u': 'eta_psi'}) 
v_eulerian = 0.5*( Ds['v'].isel(xi_v = slice(0,-1)) + Ds['v'].isel(xi_v = slice(1,None)) ).rename({'xi_v': 'xi_psi', 'eta_v': 'eta_psi'}) 
u_stokes = 0.5*( Ds['u_stokes'].isel(eta_u = slice(0,-1)) + Ds['u_stokes'].isel(eta_u = slice(1,None)) ).rename({'xi_u': 'xi_psi', 'eta_u': 'eta_psi'}) 
v_stokes = 0.5*( Ds['v_stokes'].isel(xi_v = slice(0,-1)) + Ds['v_stokes'].isel(xi_v = slice(1,None)) ).rename({'xi_v': 'xi_psi', 'eta_v': 'eta_psi'}) 
u = u_eulerian + u_stokes
v = v_eulerian + v_stokes

#get z value first, then reconstruct time varying psi depth grid
# z = 0.25*( z.isel(eta_rho = slice(0, -1), xi_rho = slice(0, -1) ) \
#          + z.isel(eta_rho = slice(1, None), xi_rho = slice(1, None) ) \
#          + z.isel(eta_rho = slice(1, None), xi_rho = slice(0, -1) ) \
#          + z.isel(eta_rho = slice(0,-1), xi_rho = slice(1,None)) ) #to psi points 

#this is probably wrong b/c sigma levels
# w = 0.25*( w.isel(eta_rho = slice(0, -1), xi_rho = slice(0, -1) ) \
#          + w.isel(eta_rho = slice(1, None), xi_rho = slice(1, None) ) \
#          + w.isel(eta_rho = slice(1, None), xi_rho = slice(0, -1) ) \
#          + w.isel(eta_rho = slice(0,-1), xi_rho = slice(1,None)) ) #to psi points
# w = 0.5*( w.isel(s_w = slice(0,-1)).values +  w.isel(s_w = slice(1, None)).values ) #to vertical rho points

#angle_psi = 0.25*( Ds.angle.isel(eta_rho = slice(0, -1), xi_rho = slice(0, -1) ) \
#         + Ds.angle.isel(eta_rho = slice(1, None), xi_rho = slice(1, None) ) \
#         + Ds.angle.isel(eta_rho = slice(1, None), xi_rho = slice(0, -1) ) \
#         + Ds.angle.isel(eta_rho = slice(0,-1), xi_rho = slice(1,None)) ).rename({'xi_rho': 'xi_psi', 'eta_rho': 'eta_psi'}) #to psi points
#uveitheta = (u + 1j*v)*np.exp(1j*angle_psi) #rotate to eastward and northward
#u_eastward  = np.real(uveitheta.isel(s_rho = -1)) #top slice
#v_northward = np.imag(uveitheta.isel(s_rho = -1)) #top slice

data = {'U': u.values, 'V': v.values} #2D velocity
dimensions = {'lon': x, 'lat': y, 'time': t }
fieldset = FieldSet.from_data(data, dimensions, transpose = False, mesh = 'flat') 

def DeleteParticle(particle, fieldset, time):
    print("Deleting particle")
    particle.delete()

recovery = {ErrorCode.ErrorOutOfBounds: DeleteParticle,
            ErrorCode.ErrorThroughSurface: DeleteParticle}

pset = ParticleSet.from_line(fieldset = fieldset, size = 1000, start = (1000, 1000), finish = (8000,1000), pclass = JITParticle )

kernels = AdvectionRK4 #+ pset.Kernel(periodicBC) 
output_file = pset.ParticleFile(name= "/work/wtorres/temp/reefParticles", outputdt = delta(seconds = 60) )
pset.execute( kernels, runtime = delta(hours = 12.0), dt = delta(seconds = 60), output_file = output_file, recovery = recovery )
output_file.export()
output_file.close()

