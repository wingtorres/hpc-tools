addpath(genpath('/home/wtorres/COAWST/Tools/mfiles'))

load('tetiaroa_grid_20.mat');
mat2roms_mw('tetiaroa_grid.mat','tetiaroa_grid.nc');
roms2swan('tetiaroa_grid.nc');
movefile('swan_coord.grd','tetiaroa_coord.grd');
movefile('swan_bathy.bot','tetiaroa_bathy.bot');
