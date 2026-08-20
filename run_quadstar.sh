#!/bin/bash

set -uo pipefail

prog_dir="/home/pi/QuadStar_Auxillary_Computer"
images_dir="/home/pi/images/QuadStar"
hang_timeout=360

cd "$prog_dir" || { echo "Error: cannot cd to $prog_dir" >&2; exit 1; }
source "$prog_dir/.venv/bin/activate" 

cleanup () {
	# echo "Cleaning up..." # is erroring with 'broken pipe'
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

		setsid "$@" >/dev/null &
		local cmd_pid=$!

		{
			sleep "$hang_timeout"
			if kill -0 "$cmd_pid" 2>/dev/null; then
				echo "$name: killed after exceeding ${hang_timeout}s (hang)" >&2
				kill -TERM -"$cmd_pid" 2>/dev/null
				sleep 10
				kill -KILL -"$cmd_pid" 2>/dev/null
			fi
		} &
		local watchdog_pid=$!

		wait "$cmd_pid" 2>/dev/null
		kill "$watchdog_pid" 2>/dev/null
		wait "$watchdog_pid" 2>/dev/null

		local elapsed=$(( $(date +%s) - start))
		if (( elapsed < interval )); then
			sleep $(( interval - elapsed ))
		fi
	done 
}

capture_interval=180
wide_capture_interval=180

zip_interval=60
solve_interval=120

worker_loop "$capture_interval" capture ./capture.sh &
sleep 5
# worker_loop "$wide_capture_interval" wide_capture ./wide_capture.sh &
sleep 5
worker_loop "$solve_interval" solve ./solve.sh &

worker_loop "$zip_interval" zip_images ./zip_images.sh &
worker_loop "$zip_interval" zip_wide_images ./zip_images.sh /home/pi/images/wide &

# wait here forever so all children are kept alive
wait 
