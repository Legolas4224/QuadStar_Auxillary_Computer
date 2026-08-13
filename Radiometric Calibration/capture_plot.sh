#beshang      !#/bin/bash
#!/bin/bash

# Takes images in a loop, then creates image histogram. image data synced back to PC
# Inputs (current): exposure time, test name, 

#Inputs (needed): exp time, num exposures, test name, camera 0 or 1, return path

#exp time should automatically pass through to filenames



source .venv/bin/activate
echo "Make sure the first arg is the exptime and the second is the capture name"
count=1
while [ $count -le 1 ]
do
    echo "======================================================================="
    echo "Iteration:  $count"
    ((count++)) # Increments the counter to avoid an infinite loop
    python src/histogram.py $1 $2
    echo " ================================= "
    echo " "
    echo "Adjust luminance now!"
    sleep 2

done
#python src/histogram.py $1
mkdir /home/pi/QuadStar_Auxillary_Computer/plots/$2
rsync -vzr /home/pi/QuadStar_Auxillary_Computer/plots/$2 thomas@10.229.169.96:/home/thomas/Documents/Code/QuadStar/Calibration/widetest
#rsync -vzr /home/pi/QuadStar_Auxillary_Computer/plots "ithomas@10.229.169.96:C:/QuadStar/"

