#!/bin/bash

PROG_DIR="/home/pi/QuadStar_Auxillary_Computer"
CAM2_DIR="/home/pi/images/wide"

CAMERA_NUMBER=1 # normally will be 1 but can be 0 for testing

folder=""

clean_up() {
	[ -d $folder ] && mv "$folder" "$folder.done"
	exit 1	
}
trap clean_up INT TERM KILL

LONG_SENSOR_MODE="4056:3040:12"
WIDE_SENSOR_MODE="4608:2592:10"


run_exposure() {
	local exposure_len_secs="$1s"
	local n=${2-1}
	folder="$CAM2_DIR/$(date '+%Y%m%d_%H%M%S')_e-"$exposure_len_secs"_g-1.0_n-$n"
	echo "exp: $exposure_len_secs, num: $n, folder: $folder"  
	mkdir -p $folder
	for i in $(seq "$n")
	do
		local flags="--camera $CAMERA_NUMBER --zsl --autofocus-mode manual --shutter $exposure_len_secs --lens-position 10.0 --gain 1.0 --awbgains 1,1  -o $folder/wide_"$i"_$(date '+%s').dng  --nopreview --immediate --mode $LONG_SENSOR_MODE "
		echo "rpicam-still $flags"
		rpicam-still $flags
	done
	mv "$folder" "$folder.done"
}


mkdir -p $CAM2_DIR
export LIBCAMERA_LOG_LEVELS=3 # limit logs to errors

run_exposure 0.25 10
run_exposure 0.5 10
run_exposure 1 5
run_exposure 2 5
run_exposure 4 5

