import sys
filename = sys.argv[1]
waveheight = float(sys.argv[2])

with open(filename, "rt") as file:
   lines =  file.readlines()
   file.close() 
   newfile = open("spec_temp.txt","w")
   newfile.write(lines[0]) #header 
   for k,line in enumerate(lines[1:]):
      hsig = min( round(0.25 + k*(waveheight - 0.25)/2, 3), waveheight)
      s = line.split()[0].rjust(10) + f"{hsig}".rjust(10) + "    " + line.split()[2] + "   " + line.split()[3] + "   " + line.split()[4] + "\n"
      newfile.write(s)
   newfile.close()
   
	
