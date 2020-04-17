function [cb]= fixplt(ax)
ax.YAxis.FontSize = 8;
ax.XAxis.FontSize = 8;

ax.Color = 'k';
ax.YAxis.Color = 'w';
ax.XAxis.Color = 'w';

lat_lon_proportions()
%set(gcf,'Color',[0,0,0]/255);
%set(gca,'color','w');

%Colorbar
cb = colorbar();
cb.Color = 'w';
cb.Box = 'off';
%Adjust colorbar position and dimensions
axpos = ax.Position;
%cb.Position(3) = 0.25*cb.Position(3); %thinner
%cb.Position(1) = axpos(1)+.3; %adjust x distance
%ax.Position = axpos;
%Rotate and fix colorbar label 
cb.Label.Interpreter = 'latex';
cb.Label.HorizontalAlignment = 'left';
cb.Label.Color = 'w';
cb.FontSize = 8;
cb.Label.FontSize = 14;
cb.Label.Position(1) = cb.Position(1)+6;
cb.Label.Rotation = 0; % to rotate the text

%xlabel(ax,'x (km)','fontsize',10);
%ylabel(ax,'y (km)','fontsize',10);
%axis image;
ax.Box = 'off';

% ax.LineWidth = 1;
end
