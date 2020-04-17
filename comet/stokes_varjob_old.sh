#!/bin/bash
#SBATCH --job-name="STOKES"
#SBATCH --output="stokes.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=24
#SBATCH --export=ALL
#SBATCH -t 01:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=walter.torres@duke.edu

MODULEPATH=$MODULEPATH:/share/apps/compute/modulefiles/applications
module purge
module load gnutools
module load intel/2016.3.210
#module load intel/2013_sp1.2.144
module load intelmpi
module load netcdf/4.3.2intelmpi
#module load python
#module load scipy

for i in {20..20..0}
do
  for j in {100..100..0}
  do
  #Edit and replace kn/gamma values then run SWAN
  u=$(echo "$i/100" | bc -l)
  ustr=$(printf "%.2f\n" $u)
  hs=$(echo "$j/100" | bc -l)
  hsstr=$(printf "%.2f\n" $hs)  
  echo "U = $ustr"
  echo "Hs = $hsstr"
  sed -i "s/q = [^ ]*/q = "$ustr"_r8/" Projects/Stokes_test/Refined/ana_m2obc.h
  sed -i "s/q = [^ ]*/q = "$ustr"_r8/" Projects/Stokes_test/Refined/ana_initial.h
  sed -i "s/PAR [^ ]*/PAR "$hsstr"/" Projects/Stokes_test/Refined/swan_stokes_test.in
  make clean
  ./coawst_stokes_ref.bash -j 8 & #need to compile for ana_m2obc.h to have effect
  wait
  mpirun -np 192 ./coawstM Projects/Stokes_test/Refined/coupling_stokes_test.in

  #Create directory name from kn/gamma values
  udir=$(echo "$i" | bc -l)
  udirstr=$(printf "%03g\n" $udir)
  hsdir=$(echo "$j" | bc -l)
  hsdirstr=$(printf "%03g\n" $hsdir)
  dirname='stokes_u_'$udirstr'_hs_'$hsdirstr
  echo "$dirname"
  
  #Create folder & move model output
  rm -rf Output/$dirname; mkdir Output/$dirname
  cp Projects/Stokes_test/Refined/ana_m2obc.h Output/$dirname
  cp Projects/Stokes_test/Refined/swan_stokes_test.in Output/$dirname 
  cp Projects/Stokes_test/Refined/ocean_stokes_test.in Output/$dirname
  mv ocean_his_stokes.nc Output/$dirname
  mv ocean_dia_stokes.nc Output/$dirname
  done
done


