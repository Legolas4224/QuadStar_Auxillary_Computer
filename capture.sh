#!/bin/bash
echo "Starting main.py"

rm /home/pi/QuadStar_Auxillary_Computer/img_median.csv
python src/main.py 0.3 	1.0 	5
python src/main.py 0.5 	1.0 	5
python src/main.py 3 	1.0 	5
python src/main.py 5 	1.0 	5
python src/auto_exposure.py

echo "All exposures captured"
