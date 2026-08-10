#!/bin/bash

PROG_DIR="/home/pi/QuadStar_Auxillary_Computer"

# DEFAULT_FLAGS="--camera 1 --immediate --autofocus-mode manual --lens-position 0.0 --gain 1.0 -e rgb -o $(date '+%Y%m%d_%H%M%S').jpg --raw --denoise off"

run_exposure() {
	local flags="--camera 1 --immediate --autofocus-mode manual --lens-position 0.0 --gain 1.0 -e rgb -o $PROG_DIR/$(date '+%Y%m%d_%H%M%S')_e-$1_g-1.0_n-${2-1}.jpg --raw --denoise off"
	echo "rpicam-still $flags"
}

run_exposure 0.5

# echo "rpicam-still $DEFAULT_FLAGS --shutter 0.5"
# rpicam-still $DEFAULT_FLAGS --shutter 0.5  
