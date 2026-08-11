#beshang      !#/bin/bash
#!/bin/bash
source .venv/bin/activate

python src/histogram.py $1
rsync -vzr /home/pi/QuadStar_Auxillary_Computer/plots thomas@10.1.1.49:/home/thomas/Pictures/Quadstar/Calibration/

