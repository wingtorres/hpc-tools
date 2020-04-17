
fname = 'ocean_his_stokes.nc';
u = ncread(fname,'u');
v = ncread(fname,'v');
ocean_time = ncread(fname,'ocean_time');

ut = diff(u,1,4);
vt = diff(v,1,4);
mt = .5*(ocean_time(2:end) + ocean_time(1:end-1));

un = zeros(size(ut,4),1);
vn = zeros(size(vt,4),1);

ut(isnan(ut))= 0;
vt(isnan(vt))= 0;

for i = 1:numel(mt)
	ur = ut(:,:,:,i);
	vr = vt(:,:,:,i);
	un(i) = norm(ur(:),2);
	vn(i) = norm(vr(:),2);
end

%disp(un)

fig = figure
plot(mt,un,'b'); hold on;
plot(mt,vn,'r');
ylabel('2 Norm');
xlabel('time');
legend('U','V');
saveas(gcf,'stokes_conv.png')


