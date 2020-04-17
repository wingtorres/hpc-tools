%MNS figures
gridname = '/work/wtorres/tetiaroa/tetiaroa_grid.nc';
hisnames='/work/wtorres/MNS/Results/ocean_his_mns_00012.nc';
%d = dir('/work/wtorres/MNS_Long/Results/');
d = dir('/work/wtorres/tetiaroa/Results');
%d = dir('/work/wtorres/tetiaroa');



x_rho = ncread(gridname,'lon_rho'); %/1e3;
y_rho = ncread(gridname,'lat_rho'); %/1e3;
x_u = ncread(gridname,'lon_u'); %/1e3;
y_u = ncread(gridname,'lat_u'); %/1e3;
x_v = ncread(gridname,'lon_v'); %/1e3;
y_v = ncread(gridname,'lat_v');

k=0;
parpool('local', 16)
parfor j = 1:numel(d)

%if startsWith(d(j).name,'ocean_his')
%if startsWith(d(j).name,'ocean_rst')
if startsWith(d(j).name,'ocean_avg')

hisname = strcat(d(j).folder,'/',d(j).name);
ocean_time = ncread(hisname,'ocean_time');
ue = ncread(hisname,'u');
us = ncread(hisname,'u_stokes');
ve = ncread(hisname,'v');
vs = ncread(hisname,'v_stokes');
ubar = ncread(hisname,'ubar');
ubar_stokes = ncread(hisname,'ubar_stokes');
vbar = ncread(hisname,'vbar');
vbar_stokes = ncread(hisname,'vbar_stokes');
zeta = ncread(hisname,'zeta');
Hs = ncread(hisname,'Hwave')

for i = 1:numel(ocean_time)
k=k+1;
%k = 2*(ocean_time(i)/300 - .25)

%u = (ubar(:,:,i) + ubar_stokes(:,:,i));
%v = (vbar(:,:,i) + vbar_stokes(:,:,i));
u = ue(:,:,end,i) + us(:,:,end,i);
v = ve(:,:,end,i) + vs(:,:,end,i);

f=figure('visible', 'off');

subplot(222); %eta
pcolor(x_rho,y_rho,zeta(:,:,i)); 
title('$\eta$ (m)','fontsize',10,'color','w')
shading flat; 
colormap(gca,cmocean('balance')); 
cb = colorbar;
%cb.Limits = [-.1 .1];
caxis([-.25 .25]); 
%set(gca,'color','k');
cb = fixplt(gca);
%cb.Label.String = '$\overline{\eta}$ (m)';

subplot(221); %Hs
pcolor(x_rho,y_rho,Hs(:,:,i)); 
title('$\eta$ (m)','fontsize',10,'color','w')
shading flat; 
colormap(gca,cmocean('amp')); 
cb = fixplt(gca);
%cb.Label.String = '$\overline{\eta}$ (m)';

subplot(223); %U
pcolor(x_u,y_u,u); 
title('U (ms^{-1})','fontsize',10,'color','w')
shading flat; 
colormap(gca,cmocean('balance')); 
caxis(.25*[-1 1]); 
set(gca,'color','k');
cb = fixplt(gca);
%cb.Label.String = '$\overline{U_{\theta}}$ (ms$^{-1}$)';

subplot(224); %V
pcolor(x_v,y_v,v); 
title('V (ms^{-1})','fontsize',10,'color','w');
shading flat; 
colormap(gca,cmocean('balance')); 
%cb = colorbar;
%cb.Limits = [-1 1];
caxis(.25*[-1 1]); 
% set(gca,'color','k');
cb = fixplt(gca);
%cb.Label.String = '$\overline{U_{r}}$ (ms$^{-1}$)';

fig = gcf;
% fig.Color = [252,250,243]/255;
fig.Color = 'k';
fig.InvertHardcopy = 'off';
%fig.Position = [275,275,725,450];

fname = sprintf('%04d.png',k);
fname = strcat(['/work/wtorres/tet_vis/',fname])
disp(fname)
print(fig,fname,'-dpng','-r300')
close(fig)
%saveas(gcf,fname)
%savefig('mns_vis')
end
end
end
