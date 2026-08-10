#!/bin/bash

PROG_DIR="/home/pi/QuadStar_Auxillary_Computer"
CAM2_DIR="/home/pi/images/wide"

CAMERA_NUMBER=0 # normally will be 1 but can be 0 for testing

run_exposure() {
	local n=${2-1}
	local folder="$CAM2_DIR/$(date '+%Y%m%d_%H%M%S')_e-$1_g-1.0_n-$n"
	mkdir -p $folder
	for i in $(seq "$n")
	do
		local flags="--camera $CAMERA_NUMBER --immediate --autofocus-mode manual --lens-position 0.0 --gain 1.0 -e rgb -o $folder/wide_$i_$(date '+%s').dng --raw --denoise off"
		echo "rpicam-still $flags"
		rpicam-still $flags
	done
	mv "$folder" "$folder.done"
}

mkdir -p $CAM2_DIR

run_exposure 0.5 5
