#beshang      !#/bin/bash
#!/bin/bash
source .venv/bin/activate
count=1
while [ $count -le 50 ]
do
    echo "======================================================================="
    echo "Iteration:  $count"
    ((count++)) # Increments the counter to avoid an infinite loop
    python src/histogram.py $1
    echo " ================================= "
    echo " "
    echo "Adjust luminance now!"
    sleep 2

done
#python src/histogram.py $1
rsync -vzr /home/pi/QuadStar_Auxillary_Computer/plots thomas@10.229.169.96:/home/thomas/Documents/Code/QuadStar/Calibration/
#rsync -vzr /home/pi/QuadStar_Auxillary_Computer/plots "ithomas@10.229.169.96:C:/QuadStar/"

