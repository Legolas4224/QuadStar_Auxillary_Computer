#!/bin/bash
# source /home/pi/QuadStar_Auxillary_Computer/.venv/bin/activate
echo "Starting main.py"

CSV_FILE="/home/pi/QuadStar_Auxillary_Computer/img_median.csv"

[ -f "$CSV_FILE" ] && rm $CSV_FILE
python src/main.py 0.05 1.0 	10
python src/main.py 0.1	1.0 	15
python src/main.py 0.25	1.0 	15
python src/main.py 0.5 	1.0 	10
python src/main.py 1 	1.0 	5
python src/main.py 5 	1.0 	5
python src/main.py 10 	1.0 	1

python src/auto_exposure.py

echo "All exposures captured"
