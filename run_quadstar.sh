#!/bin/bash

set -uo pipefail

prog_dir="/home/pi/QuadStar_Auxillary_Computer"
images_dir="/home/pi/images/QuadStar"
poll_interval=120 # seconds

cd "$prog_dir" || { echo "Error: cannot cd to $prog_dir" >&2; exit 1; }
source "$prog_dir/.venv/bin/activate" 

cleanup () {
	echo "Cleaning up..."
	kill $(jobs -p) 2>/dev/null | true
}
trap cleanup EXIT INT TERM

worker_loop() {
	local interval="$1"
	local name="$2"
	shift 2
	while true; do
		local start
		start=$(date +%s)

		"$@" > /dev/null

		local elapsed=$(( $(date +%s) - start))
		if (( elapsed < interval )); then
			sleep $(( interval - elapsed ))
		fi
	done 
}

capture_interval=180
zip_interval=120
solve_interval=120

worker_loop "$capture_interval" capture ./capture.sh &
worker_loop "$zip_interval" zip_images ./zip_images.sh &
worker_loop "$solve_interval" solve ./solve.sh &
wait

# -- Old Method
#
# while true; do
# 	echo "=== Cycle start: $(date '+%Y-%m-%d %H:%M:%S') ==="
# 
# 	./capture.sh &
# 	capture_pid=$!
# 
# 	./zip_images.sh &
# 	zip_pid=$!
# 
# 	run_solve_pass &
# 	solve_pid=$!
# 
# 	wait "$capture_pid" "$zip_pid" "$solve_pid"
# 
# 	echo "=== Cycle done ==="
# 	sleep "$poll_interval"
# done


