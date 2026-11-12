from collections import OrderedDict

def suntans_run(suntans_info):

    # run_info is the dictionary with any suntans.dat parameters changes from default. these names must match suntans.dat inputs

    # remap names for readability and file naming
    run_info = OrderedDict()
    remap = OrderedDict(amp = "A", Coriolis_f = "Φ", wavenumber_horizontal = "λ", wavenumber_vertical = "m") 
    
    for key,value in suntans_info.items():
        if key in remap:
    
            if key == "amp":
                run_info[remap[key]] = f"{value:02d}m"
    
            elif key == "Coriolis_f":
                """convert to latitude"""
                run_info[remap[key]] = f"{(180/math.pi)*math.asin(value/(2*7.29e-5)):02.0f}"
                
            elif key == "wavenumber_horizontal":
                """convert to wavelength"""
                run_info[remap[key]] = f"{2*math.pi*value**(-1):05.0f}m"
                
            else:
                run_info[remap[key]] = value

    run_name = "_".join(f"{k}_{v}" for k, v in run_info.items())

    return run_info, run_name


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