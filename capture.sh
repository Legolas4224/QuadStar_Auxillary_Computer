#!/bin/bash
echo "Starting main.py"

CSV_FILE="/home/pi/QuadStar_Auxillary_Computer/img_median.csv"

[ -f "$CSV_FILE" ] && rm $CSV_FILE
#python src/main.py 0.3 	1.0 	5
# python src/main.py 0.5 	1.0 	5
# python src/main.py 3 	1.0 	5
# python src/main.py 5 	1.0 	5
python src/main.py 0.5 1.0 3
#python src/main.py 30 1.0 5
python src/auto_exposure.py

echo "All exposures captured"
