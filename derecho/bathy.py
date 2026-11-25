from utility import *

## to find optimal slope

H = 100

# use "root_scalar" to find an equivalent Lambda to hit h(x=L) = 0
β = 0.0005
x0 = 13e3
Λ = root_scalar( bathy_slope_find, args = (β,x0), x0 = 0.02).root
x0 = equal_integral_x0(20e3, 0.02, 0.0001, -100)

L, Λ_ref, h0, β = 20_000.0, 0.02, -100.0, 0.0005
x0_ref = L + h0 / Λ_ref
Λ, x0 = match_bathy(L, Λ_ref, h0, β)
reference_area = h0 * L + 0.5 * Λ_ref * (L - x0_ref)**2
smooth_area = quad(lambda x: bathy(x, Λ, x0, β, h0), 0, L, points=[x0])[0]
print(f"Reference: Λ_ref={Λ_ref:.8f}, x0_ref={x0_ref:.6f}")
print(f"Smooth:    Λ={Λ:.10f}, x0={x0:.6f}")
print(f"h(L)={bathy(L, Λ, x0, β, h0):.3e}")
print(f"Reference area={reference_area:.6f}; smooth area={smooth_area:.6f}")
