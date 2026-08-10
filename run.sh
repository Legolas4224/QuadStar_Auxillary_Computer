#!/bin/bash

prog_dir="/home/pi/QuadStar_Auxillary_Computer"

source $prog_dir/.venv/bin/activate
$prog_dir/capture.sh &
$prog_dir/zip_images.sh &

find /home/pi/images/QuadStar/ -maxdepth 1 -type d -name "*.solve" -print0 | while IFS= read -r -d '' dir; do
	echo "Processing: $dir"
	python3 $prog_dir/src/platesolving/QuadSolver.py -f "$dir"
done
# NOTE: we can only store 1 type either .dng or .fits, which one should we store?
# 	-- We will absolutely store the stacked/solved image and data 

