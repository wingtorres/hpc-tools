#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path

import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

#os.chdir("/Users/wtorres/Documents/hpc-tools/derecho")
from submit_jobs import *
from utility import *
from jobs import *
from grid import * 
from physics import solve_flux_variable, reference_flux

## Constant energy flux

ω = 2*math.pi / (3600*12.42) #M1 tidal period
f = 1e-5
theta = math.radians(30)
amplitudes = np.array([4,8,12,16,20,])
#amplitudes = np.linspace(1,1000)

k = np.array(
    [solve_flux_variable(flux_ratio = 1000, H = 100, omega = ω, theta = theta, k = None, f = f, A = a) 
     for a in amplitudes]
    )

print(f"L = { np.round(2*np.pi*k**(-1))}")

#submission loop

path = Path("./rundata").resolve().as_posix()
homeproj = f"{os.environ['WORK']}/idealized_siw/suntans-gvc-oblique-iw/examples/internal_wave_shoaling" 
outdir = os.environ['SCRATCH'] 

for amp in [5,10,15]:
    for f in [0,1e-4]:
        
        suntans_info = OrderedDict(amp = amp, Coriolis_f = f, wavenumber_horizontal = k[-1])  
        run_info, run_name = suntans_run(suntans_info)
        print(run_name)
        
        destproj = f"{homeproj}/runs/{run_name}"
        print(homeproj, destproj)
        setup_run_directory( Path(homeproj), Path(destproj) )
#        assert False

        #modify grid if necessary
        W = domain_width_from_wave(k = k[-1], theta_deg = 30.0, n_waves=1)
        generate_grid(datadir = destproj + "/data", Nx = 200, Ny = 130, L = 20000.0, W = W)
        
        dat_path = Path(f"{destproj}/input/suntans.dat")
        print(dat_path)

        for key, value in suntans_info.items():
            vary_param(dat_path, key, value)

        cmd = [f'qsub -v suntansproj="{path}" suntans_job.pbs']
        assert False
