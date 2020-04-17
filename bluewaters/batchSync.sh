
projnames=/scratch/eot/torres/slope* 
#projnames=/scratch/eot/torres/smol*
compressdir=/scratch/eot/torres/compress
for g in $projnames
do

echo "Copying $g to LSU..."

/usr/bin/rsync --ignore-existing -avre 'sshpass -p "inyathi777_Hiraaji13!" ssh' $g wtorres@smic1.hpc.lsu.edu:/work/wtorres/annulus --exclude 'Build' # --exclude="ocean_avg_ann_000*" #--exclude="ocean_avg_ann_001*"
#/usr/bin/sshpass -p inyathi777_Hiraaji13!
#sshpass -f password
#rsync -avr -e ssh $g wtorres@smic1.hpc.lsu.edu:/work/wtorres/annulus --exclude 'Build' --exclude="ocean_avg_ann_000*" --exclude="ocean_avg_ann_001*"

#rsync -avr --password-file=/u/eot/torres/COAWST/Scripts/password $g wtorres@smic1.hpc.lsu.edu:/work/wtorres/annulus --exclude 'Build' --exclude="ocean_avg_ann_000*" --exclude="ocean_avg_ann_001*"

#break
done

