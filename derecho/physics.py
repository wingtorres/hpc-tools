"""
Internal wave calculations
"""

import math


def bvf(frequency, wavenumber, depth, coriolis):
    """
    Compute N² from the linear internal wave dispersion relation under rotation.
    
    Parameters
    ----------
    frequency  :  float  - wave frequency (rad/s)
    wavenumber : float - horizontal wavenumber (rad/m)
    depth      : float - water depth (m)
    coriolis   : float - Coriolis parameter f (rad/s)

    Returns
    -------
    N2 : float - buoyancy frequency squared (rad²/s²)
    """
    pi = math.pi
    N2 = (frequency**2 * (pi**2 + wavenumber**2 * depth**2) - (pi * coriolis)**2) \
         / (wavenumber**2 * depth**2)
    return N2

def uv(amplitude, k, theta, m, ω, coriolis, N2):
    
    """
    velocity component magnitudes for a rotating internal wave propagating
    obliquely at angle theta from the x-axis.

    Parameters
    ----------
    displacement_amplitude : float - signed peak isopycnal-displacement coefficient A [m].
    k         : float - horizontal wavenumber magnitude (rad/m)
    theta      : float - propagation angle from x-axis (rad)
    m          : float - vertical wavenumber (rad/m), = pi/H for mode-1
    frequency  : float - wave frequency omega (rad/s)
    coriolis   : float - Coriolis parameter f (rad/s)
    N2         : float - buoyancy frequency squared (rad^2/s^2)

    Returns
    -------
    u, v : horizontal velocity ampltiuders
    """

    #kinematic-pressure amplitude 
    #P = amplitude * (N2 - ω**2)/m
    
    # horizontal wavenumber components
    kx = k * math.cos(theta)
    ky = k * math.sin(theta)

    # wave phase
    #phase = kx*x + ky*y + m*z - frequency*t

    # polarization relations (from Oceananigans / standard IGW theory)
    # u: along-propagation horizontal velocity
    u = A * ω * m/k  #/ (ω**2 - coriolis**2) # *math.cos(phase)

    # v: transverse horizontal velocity — this is the Coriolis-induced component
    # it's 90 degrees out of phase with u, hence sin(phase)
    v = A *  coriolis * m/k #/ (ω**2 - coriolis**2) # *math.sin(phase)

    # vertical velocity
    w = -amplitude * ω  #* math.cos(phase)

    return u,v,w


# def uv(amplitude, x, y, z, t, k, theta, m, ω, coriolis, N2):
    
#     """
#     Polarization relations for a rotating internal wave propagating
#     obliquely at angle theta from the x-axis.

#     Parameters
#     ----------
#     amplitude  : float - pressure amplitude (Pa or nondimensional)
#     x, y, z, t : float - position and time
#     k         : float - horizontal wavenumber magnitude (rad/m)
#     theta      : float - propagation angle from x-axis (rad)
#     m          : float - vertical wavenumber (rad/m), = pi/H for mode-1
#     frequency  : float - wave frequency omega (rad/s)
#     coriolis   : float - Coriolis parameter f (rad/s)
#     N2         : float - buoyancy frequency squared (rad^2/s^2)

#     Returns
#     -------
#     u, v, w, b : horizontal, transverse, vertical velocity and buoyancy perturbation
#     """
    
#     # horizontal wavenumber components
#     kx = k * math.cos(theta)
#     ky = k * math.sin(theta)

#     # wave phase
#     phase = kx*x + ky*y + m*z - frequency*t

#     # polarization relations (from Oceananigans / standard IGW theory)
#     # u: along-propagation horizontal velocity
#     u = amplitude * k * ω  / (frequency**2 - coriolis**2) * math.cos(phase)

#     # v: transverse horizontal velocity — this is the Coriolis-induced component
#     # it's 90 degrees out of phase with u, hence sin(phase)
#     v = amplitude * k * coriolis / (frequency**2 - coriolis**2) * math.sin(phase)

#     # w: vertical velocity
#     w = amplitude * m  * ω  / (frequency**2 - N2)   * math.cos(phase)

#     # b: buoyancy perturbation
#     b = amplitude * m  * N2  / (frequency**2 - N2)  * math.sin(phase)

#     # rotate u,v back into x,y components
#     ux = u * math.cos(theta) - v * math.sin(theta)
#     uy = u * math.sin(theta) + v * math.cos(theta)

#     return ux, uy, w, b



#### Theory

def mode1_vertical_wavenumber(H):
    """Mode-1 vertical wavenumber m1 = pi/H."""
    if H <= 0:
        raise ValueError("H must be positive.")
    return math.pi / H

def reference_flux(rho0, H, omega):
    """Fixed mode-1 reference flux F0 [W/m]."""
    if rho0 <= 0 or H <= 0 or omega <= 0:
        raise ValueError("rho0, H, and omega must be positive.")
    m = mode1_vertical_wavenumber(H)
    return rho0 * H * omega**3 / (4.0 * m**3)

def solve_flux_variable(*, flux_ratio, H, omega, theta=0.0,
                        A=None, k=None, f=None, solve_for=None,
                        f_sign=1.0):
    """
    Solve

        flux_ratio = (A*m1)^2 (m1/k)^3
                     [1 - (f/omega)^2] cos(theta)

    for exactly one of A, k, or f.

    Supply the other two variables and either leave the desired variable as
    None or name it with solve_for='A', 'k', or 'f'. When solving for f,
    f_sign selects the positive (+1) or negative (-1) root.

    Returns
    -------
    float
        The requested variable in SI units.
    """
    _validate_common(H, omega, theta)
    ctheta = math.cos(theta)
    if ctheta <= 0:
        raise ValueError(
            "This solver assumes positive incoming normal flux, so cos(theta) "
            "must be positive."
        )
    if flux_ratio <= 0:
        raise ValueError("flux_ratio = Fn/F0 must be positive.")

    values = {"A": A, "k": k, "f": f}
    if solve_for is None:
        missing = [name for name, value in values.items() if value is None]
        if len(missing) != 1:
            raise ValueError("Set exactly one of A, k, or f to None.")
        solve_for = missing[0]
    elif solve_for not in values:
        raise ValueError("solve_for must be 'A', 'k', or 'f'.")

    required = [name for name in values if name != solve_for]
    if any(values[name] is None for name in required):
        raise ValueError(f"Provide values for both variables other than {solve_for}.")

    m = mode1_vertical_wavenumber(H)

    if solve_for == "A":
        if k <= 0:
            raise ValueError("k must be positive.")
        rotation = 1.0 - (f / omega)**2
        if rotation <= 0:
            raise ValueError("Solving for A requires abs(f) < omega.")
        return math.sqrt(flux_ratio * k**3 / (m**5 * rotation * ctheta))

    if solve_for == "k":
        if A <= 0:
            raise ValueError("A must be positive.")
        rotation = 1.0 - (f / omega)**2
        if rotation <= 0:
            raise ValueError("Solving for k requires abs(f) < omega.")
        return (A**2 * m**5 * rotation * ctheta / flux_ratio)**(1.0 / 3.0)

    if A <= 0 or k <= 0:
        raise ValueError("A and k must be positive.")
    radicand = 1.0 - flux_ratio * k**3 / (A**2 * m**5 * ctheta)
    if not 0.0 <= radicand < 1.0:
        raise ValueError(
            "No propagating real-f solution: the inferred 1-(f/omega)^2 "
            f"gives radicand={radicand:.6g}; it must lie in [0, 1)."
        )
    sign = 1.0 if f_sign >= 0 else -1.0
    return sign * omega * math.sqrt(radicand)


def _validate_common(H, omega, theta):
    if H <= 0 or omega <= 0:
        raise ValueError("H and omega must be positive.")
    if not math.isfinite(theta):
        raise ValueError("theta must be finite and expressed in radians.")
