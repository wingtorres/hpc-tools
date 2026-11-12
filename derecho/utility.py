import numpy as np
from scipy.special import spence
from scipy.integrate import quad
from scipy.optimize import brentq


def log_cosh(u):
    # Stable for large |u|, unlike np.log(np.cosh(u)).
    return np.logaddexp(u, -u) - np.log(2.0)

def bathy_slope_find(Λ, β = .001385, x0 = 10e3, xf = 20e3,  h0 = -100):
    """
    for optimize Lambda
    """
    #h = abs( h0 + (Λ/β)*np.log( np.cosh(β*(xf - x0)) ) )
    h = abs( bathy(xf, x0 = x0, h0 = h0, β = β, Λ = Λ) )
    #print(h)
    return h

def integral_logcosh(L, Λ, β, x0, h):
    """Integrate (Λ/β) log(cosh(β(x−x0))) + h from 0 to L."""
    if β == 0:
        raise ValueError("β must be nonzero")

    def F(u):
        a = np.abs(u)
        return np.sign(u) * (
            0.5 * a**2 - a * np.log(2)
            + 0.5 * (spence(1 + np.exp(-2 * a)) - spence(2))
        )

    return (Λ / β**2) * (F(β * (L - x0)) - F(-β * x0)) + h * L


def integral_limited_linear(L, Λ, x0, h0):
    """Integrate max(Λ(x−x0) + h0, h0) from 0 to L (L >= 0)."""
    if L < 0:
        raise ValueError("L must be nonnegative")
    if Λ >= 0:
        excess = Λ / 2 * (max(L - x0, 0)**2 - max(-x0, 0)**2)
    else:
        excess = -Λ / 2 * (max(x0, 0)**2 - max(x0 - L, 0)**2)
    return h0 * L + excess


def equal_integral_x0(L, Λ, β, h0=0):
    """Find x0 in (0, L) where log-cosh and limited-linear integrals agree."""
    if L <= 0 or β == 0 or Λ == 0 or Λ * β < 0:
        raise ValueError("Require L > 0, β != 0, and Λ and β of the same sign")

    def difference(x0):
        return (integral_logcosh(L, Λ, β, x0, h0)
                - integral_limited_linear(L, Λ, x0, h0))

    return brentq(difference, 0, L)


def reference_bathy(x, Λ, x0, h0):
    x = np.asarray(x)
    return np.maximum(h0 + Λ * (x - x0), h0)


def bathy(x, Λ, x0, β, h0):
    x = np.asarray(x)
    return np.where(x < x0, h0,
                    h0 + (Λ / β) * log_cosh(β * (x - x0)))


def match_bathy(L, Λ_ref=0.02, h0=-100.0, β=0.001385):
    """Match reference area on [0, L] while imposing bathy(L)=0.

    Reference: max(h0 + Λ_ref * (x - x0_ref), h0).
    Its transition x0_ref = L + h0 / Λ_ref follows from h_ref(L)=0.
    Returns (Λ, x0), the smooth bathymetry parameters.
    """
    if not (L > 0 and Λ_ref > 0 and h0 < 0 and β > 0):
        raise ValueError("Require L>0, Λ_ref>0, h0<0, and β>0")

    x0_ref = L + h0 / Λ_ref
    if not (0 <= x0_ref < L):
        raise ValueError("Reference transition must lie in [0, L); "
                         "increase L or Λ_ref")
    reference_area = h0 * L + 0.5 * Λ_ref * (L - x0_ref)**2

    def slope(x0):
        return -β * h0 / log_cosh(β * (L - x0))

    def smooth_area(x0):
        d = L - x0
        a = β * d
        if a < 1e-3:
            ratio = 1 / 3 + a**2 / 45  # Limit of ∫₀¹log(cosh(a*t))dt/log(cosh(a)).
        else:
            ratio = quad(lambda t: log_cosh(a * t), 0, 1)[0] / log_cosh(a)
        return h0 * L - h0 * d * ratio

    if smooth_area(0.0) < reference_area:
        raise ValueError("No solution with 0<=x0<L for these parameters")

    x0 = brentq(lambda x0: smooth_area(x0) - reference_area, 0.0, L)
    return slope(x0), x0


    ### Sandbox

    # def bathy(x, x0 = 10e3, h0 = -100, β = .001385, Λ = 0.02, method = None):
    # """
    # tapered bathymetry to be C1 continous at transition to shelf slope.
    # """

    # if method == "linear":
    #     h = (x - x0)*Λ + h0
    # else:
    #     h = (Λ/β)*np.log( np.cosh(β*(x - x0)) ) + h0

    # if np.isscalar(x):
    #     if h < h0:
    #         h = h0
    # else:
    #     print("array")
    #     h[x < x0] = h0
        
    # return h