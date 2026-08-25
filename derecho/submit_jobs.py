#!/usr/bin/env python3
"""
SUNTANS job submission script.
Varies parameters across runs and submits PBS jobs.
"""

import math
import shutil
import subprocess
import re
from pathlib import Path


# ==============================================================================
# Configuration
# ==============================================================================

PROJECT_PATH = Path("/glade/work/wtorres/idealized_siw/suntans-gvc-oblique-iw/examples/T_M1")
BASE_RUN     = "rundata"
MFILES_PATH  = PROJECT_PATH / "mfiles"

# Parameter sweep: list of (latitude,) tuples — extend as needed
LATITUDES = [0, 10]


# ==============================================================================
# Helpers
# ==============================================================================

OMEGA = 7.2921159e-5  # Earth's rotation rate (rad/s)

def coriolis(latitude_deg: float) -> float:
    """Return the Coriolis parameter f (s⁻¹) for a given latitude in degrees."""
    return 2 * OMEGA * math.sin(math.radians(latitude_deg))


def vary_param(input_file: Path, param: str, value) -> None:
    """
    Replace the value of `param` in a SUNTANS-style dat file.
    Matches lines like:  param_name   <value>   [optional comment]
    and replaces only the value token, preserving spacing and comments.
    """
    text = input_file.read_text()
    pattern = rf'^({re.escape(param)}\s+)\S+'
    replacement = rf'\g<1>{value}'
    new_text, n = re.subn(pattern, replacement, text, flags=re.MULTILINE)

    if n == 0:
        raise ValueError(f"Parameter '{param}' not found in {input_file}")

    input_file.write_text(new_text)
    print(f"  {param:20s} → {value}")


def setup_run_directory(src: Path, dst: Path) -> None:
    """Copy base run directory and associated source files."""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    # Copy header/source files and Makefile from project root
    for pattern in ("*.h", "*.c", "Makefile"):
        for f in PROJECT_PATH.glob(pattern):
            shutil.copy2(f, dst)

    print(f"  Run directory ready: {dst}")


def build_grid(run_path: Path, suntans_file: Path) -> None:
    """Call MATLAB to build the idealized grid."""
    cmd = [
        "matlab", "-batch",
        f"addpath('{MFILES_PATH}'); idealized_grid('{run_path}', '{suntans_file}')"
    ]
    subprocess.run(cmd, check=True)


def submit_job(run_path: Path) -> subprocess.CompletedProcess:
    """Submit a PBS job from within the run directory."""
    result = subprocess.run(
        ["qsub", "suntans_run.pbs"],
        cwd=run_path,
        capture_output=True,
        text=True,
        check=True,
    )
    job_id = result.stdout.strip()
    print(f"  Submitted job: {job_id}")
    return result


# ==============================================================================
# Main sweep
# ==============================================================================

def main():
    base_path = PROJECT_PATH / BASE_RUN

    for latitude in LATITUDES:
        print(f"\n{'='*60}")
        print(f"Latitude: {latitude}°")
        print(f"{'='*60}")

        # --- directories ---
        run_name = f"rundata_f_{latitude}"
        run_path = PROJECT_PATH / run_name
        suntans_file = run_path / "suntans.dat"

        # setup_run_directory(base_path, run_path)   # uncomment to copy dirs

        # --- compute & apply parameters ---
        f = coriolis(latitude)
        print("Parameters:")
        vary_param(suntans_file, "Coriolis_f", f"{f:.10e}")
        
        # vary_param(suntans_file, "H", H)           # add more as needed

        # --- grid build (MATLAB) ---
        # build_grid(run_path, suntans_file)         # uncomment if needed

        # --- submit ---
        # submit_job(run_path)                       # uncomment to submit

if __name__ == "__main__":
    main()
