import numpy as np
import histogram as hist
import radiometric_calibration as RC
import sys
from datetime import datetime, timezone
import glob
import shutil 
import terminal_plotter as tp
import time

#exp = float(sys.argv[1])
#capture_name = sys.argv[2]
#print(f"Capturing {exp}s Image...\n")
#stats_dict = hist.capture_to_histo(exp, capture_name)
#print("Capture Complete\n==============")
#print(f"Median: {stats_dict['Median']}\nMean: {stats_dict['Mean']}")

def main(exposure_time, test_name=f"{exposure_time}"+f"{datetime.now()}", send_to_me=True, make_histo=True, wide_cam=False, demosaic=True) :
    print("Running image sensor calibration - don't forget to start OPM measurements!")
    print(f"Capturing image, exposure: {exposure_time}s")

    from main import main_manual as capture # do this here because it only works on rpi so we don't want to run it always
    
    image_dir = capture(exposure_time, 1.0, 1, wide_cam=wide_cam) # takes image and returns save path
    print(f"Image saved as: {image_dir}")                                    
    files = sorted(glob.glob(f"{image_dir}/*"))         # finds files in image dir 
    if not demosaic : 
        image = hist.load_tiff(files[0]) 
    else : 
        image = RC.demosaic
    
    ROI_array = hist.extract_ROI(image)
    tp.live_plot(ROI_array)
    #plot_path, stats = hist.plot_histogram(ROI_array, f"{capture_name}", xlog=False, ylog=True) # plots the histogram of the image, including adding ROI. calculates image stats
    #                                                                      
    #print("plot path", plot_path)                                       
    #shutil.copy(image_path, f"{plot_path}_full.tiff")           # copies the image to the same dir as the plot and cropped image
    #print("Image file and histogram copied to plots dir")
    #return stats

def live(exposure_time, test_name=f"{exposure_time}"+f"{datetime.now()}", send_to_me=True, make_histo=True, wide_cam=False, demosaic=True) :
    print("Running image sensor calibration - don't forget to start OPM measurements!")
    print(f"Capturing image, exposure: {exposure_time}s")

    from main import main_manual as capture # do this here because it only works on rpi so we don't want to run it always
    run = True

    while run == True :

        image_dir = capture(exposure_time, 1.0, 1, wide_cam=wide_cam) # takes image and returns save path
        print(f"Image saved as: {image_dir}")                                    
        files = sorted(glob.glob(f"{image_dir}/*"))         # finds files in image dir 
        if not demosaic : 
            image = hist.load_tiff(files[0]) 
        else : 
            image = RC.demosaic(files[0])
        
        ROI_array = hist.extract_ROI(image)
        tp.live_plot(ROI_array)
        time.sleep(0.5)

def load(filepath, demosaic=True) :
    run = True
    
    while run == True :

        #image_dir = capture(exposure_time, 1.0, 1, wide_cam=wide_cam) # takes image and returns save path
        #print(f"Image saved as: {image_dir}")                                    
        files = sorted(glob.glob(f"{filepath}/*"))         # finds files in image dir 
        if not demosaic : 
            image = hist.load_tiff(files[0]) 
        else : 
            image = RC.demosaic(files[0])
        
        ROI_array = hist.extract_ROI(image)
        tp.live_plot(ROI_array)
        time.sleep(0.5)

live(0.1, "test") 