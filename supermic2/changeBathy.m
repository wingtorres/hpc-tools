function [] = changeBathy(originalBathy,newBathy,offset)
h0 = ncread(originalBathy,'h');
h = h0 + str2double(offset)/100;
ncwrite(newBathy,'h',h);

addpath('/home/wtorres/COAWST/Tools/mfiles/mtools')
roms2swan(newBathy)

disp(newBathy)
end

