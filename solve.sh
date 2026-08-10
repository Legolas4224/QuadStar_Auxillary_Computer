#!/bin/bash 

prog_dir="/home/pi/QuadStar_Auxillary_Computer"
images_dir="/home/pi/images/QuadStar"

clean_fits() {
	echo "Cleaning up all *-fits from $images_dir"
	# rm -rf "$images_dir"/*-fits # simple way
	find "$images_dir" -maxdepth 1 -type d -name "*-fits" -exec rm -rf {} +
}
trap clean_fits EXIT

echo "Running solve.sh"
find "$images_dir" -maxdepth 1 -type d -name "*.solve" -print0 |
while IFS= read -r -d '' dir; do
	echo "Processing $dir"
	python3 "$prog_dir/src/platesolving/QuadSolver.py" -f "$dir"		
done


