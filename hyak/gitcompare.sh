cd $WORKDIR/opt/SUNTANS

dir1=origin/derecho:suntans-gvc-oblique-iw/examples/oblique_internal_wave/initialization.c #main_dir2=origin/hyak:examples/oblique-internal-wave #main
dir2=origin/hyak:examples/oblique_internal_wave/initialization.c #main

git diff -G"." --diff-filter=M $dir1 $dir2 '*.c' ':!._*' # | grep ^+ #to show only changed lines cd ~/hpc-tools/hyak
