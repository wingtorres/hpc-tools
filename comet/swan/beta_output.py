#!/opt/python/bin/python
import numpy as np
import os
import glob
import shutil
import re
import fileinput, sys

#find alpha value and change it!
regexp=re.compile(r'BREAKING.*?([0-9.-]+)')
alpha = [];
with open('mns_parm.swn') as f:
	for line in f:
		match = regexp.match(line)
		if match:
			alpha.append(match.group(1))
print(alpha[0])
alpha_old = float(alpha[0]);
da = .2; #how much to change alpha by
alpha_new = alpha_old - da;
print(alpha_new)
brkstr = 'BREAKING ' + 'BKD ' + str(round(alpha_old,2)) 
#print(brkstr)
newstr = 'BREAKING ' + 'BKD ' + str(round(alpha_new,2));
for line in fileinput.input('mns_parm.swn',inplace=1):
	line = re.sub(brkstr,newstr,line.rstrip())
	print(line)

#newest = max(glob.iglob('*.out'), key=os.path.getctime) #fetch most recent .out file
#dirname = newest[5:13]#folder name is run ID
dirname = 'mns_bkd_alpha_' + str(int(alpha_old*100)); 
source = os.listdir('/oasis/scratch/comet/wtorres/temp_project/SWAN');
if os.path.exists(dirname):
        shutil.rmtree(dirname) #delete folder in case it exists already
os.makedirs(dirname)   #create new folder for output
shutil.copy2('mns_parm.swn',dirname) #put input file into folder
for files in source:
        if files.endswith('.table'):
                shutil.copy2(files,dirname) #put station output into folder

test = 'Output/' + dirname
if os.path.exists(test):
        shutil.rmtree(test)
shutil.move(dirname,'Output/') #put model run in Output directory

###################################################


