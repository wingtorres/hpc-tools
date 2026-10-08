#!/usr/bin/env python3
"""
generate_grid.py
----------------
Generate Cartesian grid files (points.dat, cells.dat, edges.dat) for the
quad version of SUNTANS, given a 2-D (x, y, depth) domain and wave parameters.

The grid is uniform with dx = L/Nx and dy = W/Ny.  Periodic, open, and wall
boundary conditions are supported on all four sides.

Usage
-----
    from generate_grid import generate_grid, domain_width_from_wave

    W = domain_width_from_wave(k=0.05, theta_deg=15.0, n_waves=1)
    generate_grid(
        datadir = "rundata",
        Nx      = 200,
        Ny      = 130,
        L       = 4000.0,
        W       = W,
        west    = "velocity",
        east    = "wall",
        north   = "periodic",
        south   = "periodic",
    )

Boundary type strings
---------------------
    "wall"        -> mark = 1   (solid free-slip)
    "velocity"    -> mark = 2   (velocity specified)
    "freesurface" -> mark = 3   (free-surface specified)
    "periodic"    -> mark = 5 during construction, set to 0 afterwards
    "internal"    -> mark = 0   (interior / computational)
"""

import math
import numpy as np
from pathlib import Path


# ---------------------------------------------------------------------------
# Boundary-type helpers
# ---------------------------------------------------------------------------

_BTYPE = {
    "wall":        1,
    "velocity":    2,
    "freesurface": 3,
    "periodic":    5,
    "internal":    0,
}

def _bmark(name: str) -> int:
    key = name.strip().lower()
    if key not in _BTYPE:
        raise ValueError(
            f"Unknown boundary type '{name}'. "
            f"Choose from: {list(_BTYPE.keys())}"
        )
    return _BTYPE[key]


# ---------------------------------------------------------------------------
# Domain-width helper
# ---------------------------------------------------------------------------

def domain_width_from_wave(k: float, theta_deg: float, n_waves: int = 1) -> float:
    """
    Return the longshore domain width W so that exactly n_waves fit in
    the periodic direction.

        W = n * lambda_y = n * 2*pi / (k * sin(theta))

    Parameters
    ----------
    k         : horizontal wavenumber (rad/m)
    theta_deg : angle of incidence in degrees (0 = shore-normal)
    n_waves   : number of longshore wavelengths to include

    Returns
    -------
    W : float  domain width (m)
    """
    theta = math.radians(theta_deg)
    if abs(math.sin(theta)) < 1e-12:
        raise ValueError(
            "theta = 0 means the wave is shore-normal; "
            "the longshore wavelength is infinite. "
            "Set W manually instead."
        )
    return n_waves * 2 * math.pi / (k * math.sin(theta))


# ---------------------------------------------------------------------------
# Main grid generator
# ---------------------------------------------------------------------------

def generate_grid(
    datadir: str,
    Nx: int,
    Ny: int,
    L: float,
    W: float,
    west:  str = "velocity",
    east:  str = "wall",
    north: str = "periodic",
    south: str = "periodic",
) -> None:
    """
    Build and write SUNTANS quad-grid files to *datadir*.

    Node ordering matches MATLAB (x-major / column-major):
    nodes iterate over all x at y=0, then all x at y=dy, etc.

    Parameters
    ----------
    datadir : output directory (created if absent)
    Nx, Ny  : number of cells in x and y
    L, W    : domain dimensions (m)
    west / east / north / south : boundary type strings (see module docstring)
    """
    datadir = Path(datadir)
    datadir.mkdir(parents=True, exist_ok=True)

    west_mark  = _bmark(west)
    east_mark  = _bmark(east)
    north_mark = _bmark(north)
    south_mark = _bmark(south)

    dx = L / Nx
    dy = W / Ny

    per_x = (west_mark == 5) and (east_mark  == 5)
    per_y = (north_mark == 5) and (south_mark == 5)

    # -----------------------------------------------------------------------
    # Node (point) coordinates
    # Use "xy" indexing so the flat order is x-major (matches MATLAB ndgrid).
    # XP shape: (Ny+1, Nx+1)  ->  ravel() gives all x at y=0, then y=dy, ...
    # -----------------------------------------------------------------------
    xp_1d = np.linspace(0, L, Nx + 1)
    yp_1d = np.linspace(0, W, Ny + 1)
    XP, YP = np.meshgrid(xp_1d, yp_1d, indexing="xy")   # (Ny+1, Nx+1)

    xp = XP.ravel()
    yp = YP.ravel()
    Np = len(xp)

    # node_idx[j, i] -> flat index of node at (x=i*dx, y=j*dy)
    node_idx = np.arange(Np).reshape(Ny + 1, Nx + 1)

    # -----------------------------------------------------------------------
    # Cell centres — keep "ij" indexing internally for cell/edge logic
    # cell_idx[i, j] -> flat index of cell at (xv[i], yv[j])
    # -----------------------------------------------------------------------
    xv_1d = xp_1d[:-1] + dx / 2
    yv_1d = yp_1d[:-1] + dy / 2
    XV, YV = np.meshgrid(xv_1d, yv_1d, indexing="ij")   # (Nx, Ny)
    xv = XV.ravel()
    yv = YV.ravel()
    Nc = len(xv)

    cell_idx = np.arange(Nc).reshape(Nx, Ny)

    # -----------------------------------------------------------------------
    # Cell connectivity: four corner node indices per cell (SW NW NE SE)
    # node_idx is [j, i] so access as node_idx[J, I]
    # -----------------------------------------------------------------------
    I, J = np.meshgrid(np.arange(Nx), np.arange(Ny), indexing="ij")
    cells = np.stack([
        node_idx[J,   I  ],   # SW
        node_idx[J+1, I  ],   # NW
        node_idx[J+1, I+1],   # NE
        node_idx[J,   I+1],   # SE
    ], axis=-1).reshape(Nc, 4)

    # -----------------------------------------------------------------------
    # Neighbours (up to 4): West, North, East, South
    # -----------------------------------------------------------------------
    neigh = -np.ones((Nc, 4), dtype=int)

    # West
    iw = I - 1
    if per_x:
        mask = np.ones_like(I, dtype=bool)
        neigh[mask.ravel(), 0] = cell_idx[iw[mask] % Nx, J[mask]]
    else:
        mask = iw >= 0
        neigh[mask.ravel(), 0] = cell_idx[iw[mask], J[mask]]

    # North
    jn = J + 1
    if per_y:
        mask = np.ones_like(J, dtype=bool)
        neigh[mask.ravel(), 1] = cell_idx[I[mask], jn[mask] % Ny]
    else:
        mask = jn < Ny
        neigh[mask.ravel(), 1] = cell_idx[I[mask], jn[mask]]

    # East
    ie = I + 1
    if per_x:
        mask = np.ones_like(I, dtype=bool)
        neigh[mask.ravel(), 2] = cell_idx[ie[mask] % Nx, J[mask]]
    else:
        mask = ie < Nx
        neigh[mask.ravel(), 2] = cell_idx[ie[mask], J[mask]]

    # South
    js = J - 1
    if per_y:
        mask = np.ones_like(J, dtype=bool)
        neigh[mask.ravel(), 3] = cell_idx[I[mask], js[mask] % Ny]
    else:
        mask = js >= 0
        neigh[mask.ravel(), 3] = cell_idx[I[mask], js[mask]]

    # -----------------------------------------------------------------------
    # Edges
    # U-edges: vertical (normal in x),  at x = i*dx,  y-centre = (j+0.5)*dy
    # V-edges: horizontal (normal in y), at y = j*dy,  x-centre = (i+0.5)*dx
    # -----------------------------------------------------------------------

    # --- U-edges ---
    iu, ju = np.meshgrid(np.arange(Nx + 1), np.arange(Ny), indexing="ij")
    iu_f = iu.ravel(); ju_f = ju.ravel()

    n1_u = node_idx[ju_f,   iu_f  ]
    n2_u = node_idx[ju_f+1, iu_f  ]

    mark_u = np.zeros(len(iu_f), dtype=int)
    mark_u[iu_f == 0]  = west_mark
    mark_u[iu_f == Nx] = east_mark

    g0_u = -np.ones(len(iu_f), dtype=int)   # left cell  (i-1)
    g1_u = -np.ones(len(iu_f), dtype=int)   # right cell (i)

    il = iu_f - 1
    ir = iu_f
    if per_x:
        g0_u[:] = cell_idx[il % Nx, ju_f]
        g1_u[:] = cell_idx[ir % Nx, ju_f]
    else:
        mask_l = il >= 0
        mask_r = ir < Nx
        g0_u[mask_l] = cell_idx[il[mask_l], ju_f[mask_l]]
        g1_u[mask_r] = cell_idx[ir[mask_r], ju_f[mask_r]]

    # --- V-edges ---
    iv, jv = np.meshgrid(np.arange(Nx), np.arange(Ny + 1), indexing="ij")
    iv_f = iv.ravel(); jv_f = jv.ravel()

    n1_v = node_idx[jv_f,   iv_f  ]
    n2_v = node_idx[jv_f,   iv_f+1]

    mark_v = np.zeros(len(iv_f), dtype=int)
    mark_v[jv_f == 0]  = south_mark
    mark_v[jv_f == Ny] = north_mark

    g0_v = -np.ones(len(iv_f), dtype=int)   # south cell (j-1)
    g1_v = -np.ones(len(iv_f), dtype=int)   # north cell (j)

    jd  = jv_f - 1
    ju2 = jv_f
    if per_y:
        g0_v[:] = cell_idx[iv_f, jd  % Ny]
        g1_v[:] = cell_idx[iv_f, ju2 % Ny]
    else:
        mask_d  = jd  >= 0
        mask_u2 = ju2 < Ny
        g0_v[mask_d]  = cell_idx[iv_f[mask_d],  jd[mask_d]]
        g1_v[mask_u2] = cell_idx[iv_f[mask_u2], ju2[mask_u2]]

    # --- Concatenate ---
    edges_n1   = np.concatenate([n1_u,   n1_v])
    edges_n2   = np.concatenate([n2_u,   n2_v])
    edges_mark = np.concatenate([mark_u, mark_v])
    edges_g0   = np.concatenate([g0_u,   g0_v])
    edges_g1   = np.concatenate([g1_u,   g1_v])

    # Remove duplicate periodic boundary edges (x==L or y==W with mark==5)
    xe_mid = (xp[edges_n1] + xp[edges_n2]) / 2
    ye_mid = (yp[edges_n1] + yp[edges_n2]) / 2
    keep = ~(((edges_mark == 5) & np.isclose(xe_mid, L)) |
             ((edges_mark == 5) & np.isclose(ye_mid, W)))
    edges_n1   = edges_n1[keep]
    edges_n2   = edges_n2[keep]
    edges_mark = edges_mark[keep]
    edges_g0   = edges_g0[keep]
    edges_g1   = edges_g1[keep]
    Ne = len(edges_n1)

    # Periodic interior edges become type 0
    edges_mark[edges_mark == 5] = 0

    # SUNTANS requires grad[0] != -1 for open-boundary edges
    swap = (edges_g0 == -1) & (edges_g1 != -1)
    edges_g0[swap], edges_g1[swap] = edges_g1[swap].copy(), -1

    # -----------------------------------------------------------------------
    # Write output files (0-indexed)
    # -----------------------------------------------------------------------

    # cells.dat: nv xv yv c0 c1 c2 c3 n0 n1 n2 n3
    cells_path = datadir / "cells.dat"
    with open(cells_path, "w") as f:
        for k in range(Nc):
            c  = cells[k] - 1
            nb = neigh[k].copy()
            nb[nb != -1] -= 1
            f.write(
                f"4 {xv[k]:.10e} {yv[k]:.10e} "
                f"{c[0]} {c[1]} {c[2]} {c[3]} "
                f"{nb[0]} {nb[1]} {nb[2]} {nb[3]}\n"
            )

    # points.dat: x y marker
    points_path = datadir / "points.dat"
    with open(points_path, "w") as f:
        for k in range(Np):
            f.write(f"{xp[k]:.10e} {yp[k]:.10e} 0\n")

    # edges.dat: n1 n2 mark grad0 grad1
    edges_path = datadir / "edges.dat"
    with open(edges_path, "w") as f:
        for k in range(Ne):
            n1 = int(edges_n1[k]) - 1
            n2 = int(edges_n2[k]) - 1
            mk = int(edges_mark[k])
            g0 = int(edges_g0[k]); g0 = g0 - 1 if g0 != -1 else -1
            g1 = int(edges_g1[k]); g1 = g1 - 1 if g1 != -1 else -1
            f.write(f"{n1} {n2} {mk} {g0} {g1}\n")

    print(
        f"Grid written to {datadir}/\n"
        f"  Cells : {Nc}  ({Nx} x {Ny})\n"
        f"  Points: {Np}  ({Nx+1} x {Ny+1})\n"
        f"  Edges : {Ne}\n"
        f"  dx = {dx:.4f} m,  dy = {dy:.4f} m"
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SUNTANS quad grid files.")
    parser.add_argument("--datadir", default="rundata")
    parser.add_argument("--Nx",     type=int,   default=200)
    parser.add_argument("--Ny",     type=int,   default=130)
    parser.add_argument("--L",      type=float, default=4000.0, help="Domain length (m)")
    parser.add_argument("--W",      type=float, default=None,   help="Domain width (m)")
    parser.add_argument("--k",      type=float, default=0.05,   help="Horizontal wavenumber (rad/m)")
    parser.add_argument("--theta",  type=float, default=15.0,   help="Angle of incidence (degrees)")
    parser.add_argument("--n",      type=int,   default=1,      help="Number of longshore wavelengths")
    parser.add_argument("--west",   default="velocity")
    parser.add_argument("--east",   default="wall")
    parser.add_argument("--north",  default="periodic")
    parser.add_argument("--south",  default="periodic")
    args = parser.parse_args()

    W = args.W
    if W is None:
        W = domain_width_from_wave(args.k, args.theta, args.n)
        print(f"Computed W = {W:.4f} m  (k={args.k}, theta={args.theta}°, n={args.n})")

    generate_grid(
        datadir = args.datadir,
        Nx      = args.Nx,
        Ny      = args.Ny,
        L       = args.L,
        W       = W,
        west    = args.west,
        east    = args.east,
        north   = args.north,
        south   = args.south,
    )


def read_points(filepath: str, Nx: int, Ny: int):
    """
    Read points.dat and reshape into 2D coordinate arrays.

    Parameters
    ----------
    filepath : path to points.dat
    Nx, Ny   : number of cells in x and y
               (grid has Nx+1 x Ny+1 nodes)

    Returns
    -------
    X, Y : np.ndarray of shape (Nx+1, Ny+1)
    """
    data = np.loadtxt(filepath)   # (Np, 3)  columns: x, y, marker
    xp = data[:, 0]
    yp = data[:, 1]

    # points.dat is written x-major (all x at y=0, then y=dy, ...)
    # reshape to (Ny+1, Nx+1) then transpose to (Nx+1, Ny+1)
    X = xp.reshape(Ny + 1, Nx + 1).T
    Y = yp.reshape(Ny + 1, Nx + 1).T

    return X, Y
