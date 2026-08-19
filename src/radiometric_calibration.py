import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from pprint import pprint
from histogram import load_tiff, plot_histogram
import histogram as hist
from datetime import datetime, timedelta
import sys
import terminal_plotter as tp
from iris_control import Iris
from light_measure import LightMeasure
import os
import time

def demosaic(img_path) : #, output_path) :
    import cv2
    # 1. Load the raw TIFF image exactly as it is stored (grayscale + native bit depth)
    # IMREAD_ANYDEPTH handles 8-bit, 12-bit, or 16-bit TIFF files natively.
    raw_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH)
    # 2. Convert the Bayer pattern to standard BGR color
    # Change COLOR_BAYER_RG2BGR to match your specific camera sensor array if needed (e.g., BG, GR, GB)
    color_img = cv2.cvtColor(raw_img, cv2.COLOR_BAYER_RG2BGR)
    #print(f"Image successfully demosaiced")
    # 3. Save the debayered RGB image 
    #cv2.imwrite(output_path, color_img)
    return color_img

def testdemosaic(path):
    print(f"Demosaicing: {path}")
    print(f"Exists: {os.path.exists(path)}")

    raw_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    print(f"Loaded: {raw_img is not None}")
    if raw_img is not None:
        print(f"Shape: {raw_img.shape}")
        print(f"Dtype: {raw_img.dtype}")

    color_img = cv2.cvtColor(raw_img, cv2.COLOR_BAYER_RG2BGR)
    return color_img


def combine_data(csv_path, image_dir) : # This looks through all the images and finds the closest datapoint from the csv. It then makes a dictionary with all the relevant info
    #start_time = 0
    #end_sample
    df = pd.read_csv(csv_path, skiprows=14)
    df["time"] = pd.to_timedelta(df["Time of day (hh:mm:ss) "])
    #print(df)
    
    files = sorted(glob.glob(f"{image_dir}/*.tiff"))
    print(f"Found {len(files)} image files")
    files_dict = {}
    for file in files:
        
        delimited_filename = file.split("_")
        
        if delimited_filename[-1] == "full.tiff" :

            # Get timedelta since midnight from image
            time = delimited_filename[-2]
            dayhours,mins,secs = time.split(":")
            hours = dayhours.split("-")[-1]
            image_timedelta = pd.to_timedelta(f"{hours}:{mins}:{secs}")

            # Find closest CSV timestamp
            idx = (df["time"] - image_timedelta).abs().idxmin()
            
            row = df.loc[idx]
            #print(f"time: {row["time"]}")
            #print(f"image time: {image_timedelta}")
            time_difference = abs(row["time"]-image_timedelta)
            if time_difference > timedelta(seconds=1) :
                print(f"Delta too large between image and measurement. Not including datapoint")
            else :


                #print(f"Time delta: {time_difference}")
                #print(f"Found closest match for image {file}:")#\n{row}\n--------")
            
                power = row["Power (W)"]
                irradiance = row["Irradiance (W/cm²)"]
                power_dbm = row["Power (dBm)"]
                roi_file = file.replace("_full", "")
                files_dict[time] = [file, roi_file, power, irradiance, power_dbm]
    #pprint(files_dict)
    print(f"Images successfully correlated with OPM Log.")
    return files_dict


def calc_stats(files_dict) :
    image_list = []
    median_list = []
    irradiance_list = []

    mean_list_R = []
    mean_list_G = []
    mean_list_B = []

    median_list_R = []
    median_list_G = []
    median_list_B = []

    for entry in files_dict.values() :
        image = entry[1]
        image = demosaic(image)
        img_array = image
        R_mean, G_mean, B_mean = np.mean(img_array, axis=(0,1))
        R_median, G_median, B_median = np.median(img_array, axis=(0,1))
        #print(f"Red mean: {R_mean}")
        #print(f"Green mean: {G_mean}")
        #print(f"Blue mean: {B_mean}")
        irradiance = entry[3]
        if irradiance == np.inf :
            pass
        elif irradiance > 0.00025 :
            pass
        #elif irradiance == 0.0000 :
        #    pass
        else :
            image_list.append(image)
            irradiance_list.append(irradiance)
           
            mean_list_R.append(R_mean)
            mean_list_G.append(G_mean)
            mean_list_B.append(B_mean)
        
            median_list_R.append(R_median)
            median_list_G.append(G_median)
            median_list_B.append(B_median)
    
    stats_dict = {
        #"image" : image_list,
        #"Median ADU" : median_list,
        "Mean R" : mean_list_R,
        "Mean G" : mean_list_G,
        "Mean B" : mean_list_B,
        "Median R" : median_list_R,
        "Median G" : median_list_G,
        "Median B" : median_list_B,
        "Irradiance (W/cm^2)" : irradiance_list
    }

    
    stats_df = pd.DataFrame(stats_dict)
    #print("stats df" , stats_df)
    return stats_df

def file_gui(input_prompt, is_dir=True, filetype=[("CSV Files", "*.csv")]) :
    import tkinter as tk
    from tkinter import filedialog

    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open the directory chooser dialog box
    if is_dir :
        selected_path = filedialog.askdirectory(
            title=f"{input_prompt}",
            initialdir="/home/thomas/Documents/Code/QuadStar/Calibration/plots/"
        )
    else :
        selected_path = filedialog.askopenfilename(
            title=f"{input_prompt}",
            initialdir="/home/thomas/Documents/Code/QuadStar/Calibration/OPM-Logs/", # Optional: Sets the starting directory
            filetypes = filetype
        )

    # Print or process the selected string path
    if selected_path :
        print(f"Selected directory: {selected_path}")
        return selected_path  
    else:
        print("User cancelled the operation.")

def rsync_files(source, destination) :
    import subprocess
    # Define the command as a list of arguments
    command = [
        "rsync",
        "-avz",        # Archive mode, verbose, compress data
        #"--delete",    # Delete extraneous files from dest dirs
        source,
        destination
    ]
    
    try:
        # execute the command and wait for it to complete
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Rsync completed successfully!")
        print("Output:\n", result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Rsync failed with exit code {e.returncode}")
        print("Error output:\n", e.stderr)




#demosaic("/home/thomas/Documents/Code/QuadStar/Calibration/plots/0.5/Image-Mean27970.8592_ROI(100, 100)_0.5_12-8-15:58:52.tiff", "/home/thomas/Documents/Code/QuadStar/Calibration/DebayerTest/test.tiff")


def adjust_light_source(exposure_time) : # This function is to work out how bright the light source should be for a run of a given exp time
    from main import main_manual as capture
    wide_cam = False
    iris = Iris(2)
    light_measure = LightMeasure()
    stats = {
        "irradiance" : [],
        "median_R" : [],
        "median_G" : [],
        "median_B" : [],
        "exp_time" : exposure_time,
    }
    
    files = []
    
    iris.set_max()
    time.sleep(0.5)
    irrad = light_measure.read_irradiance()
    print(f"Irradiance (W/cm^2): {irrad}")
    image_dir = capture(exposure_time, 1.0, 1, wide_cam=wide_cam) # takes image and returns save path
    print(f"Image saved as: {image_dir}")  
    files.append(image_dir)
    image_file = image_dir+"/"
    # rsync_files(image_file, rsync_to)
    demosaic_image = True                                    
    files = [f"{image_dir}/{f}" for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    #sorted(glob.glob(image_file))         # finds files in image dir 
    print(files[0])
    if demosaic_image == False : 
        image = hist.load_tiff(files[0]) 
    else : 
        image = demosaic(files[0])
        print("demosaiced image")
    ROI_array = hist.extract_ROI(image)
    tp.live_plot(ROI_array)

    red_pixels = ROI_array[:,:, 0].ravel()
    green_pixels = ROI_array[:,:, 1].ravel()
    blue_pixels = ROI_array[:,:, 2].ravel()

    stats["median_R"].append(np.median(red_pixels))
    stats["median_G"].append(np.median(green_pixels))
    stats["median_B"].append(np.median(blue_pixels))
    stats["irradiance"].append(irrad)

    deltamax_red = np.max(red_pixels) - np.min(red_pixels)
    deltamax_green = np.max(green_pixels) - np.min(green_pixels)
    deltamax_blue = np.max(blue_pixels) - np.min(blue_pixels)
    print(f"Deltamaxes: r({deltamax_red}), g({deltamax_green}), b({deltamax_blue})")

    if stats["median_R"][-1] > (2**16 -1000):
        print("Red Channel Clipped")
    if stats["median_G"][-1] > (2**16 -1000):
        print("Green Channel Clipped")
    if stats["median_B"][-1] > (2**16 - 1000) :
        print("Blue Channel Clipped")

    else :
        print("No channels clipped")


    #print("Capture and sync complete")
    #print(f"Stats dict: {stats}")
    #live_analyse(stats)
    #tp.plot_medians(stats)




def collect_data(exposure_time, num_exposures, test_name, rsync_to="~/Documents/Code/QuadStar/Calibration/" ,send_to_me=True, make_histo=True, wide_cam=False, demosaic_image=True) :
    input("Press ENTER to begin capture. Make sure OPM is logging first!...")
    print("Running image sensor calibration!")
    print(f"Capturing image, exposure: {exposure_time}s")

    from main import main_manual as capture # do this here because it only works on rpi so we don't want to run it always

    iris = Iris(num_exposures)
    light_measure = LightMeasure()
    stats = {
        "irradiance" : [],
        "median_R" : [],
        "median_G" : [],
        "median_B" : [],
        "exp_time" : exposure_time,
    }
    
    files = []
    for i in range(0, num_exposures) :
        iris.set(i)
        time.sleep(0.5)
        irrad = light_measure.read_irradiance()
        print(f"Irradiance (W/cm^2): {irrad}")
        image_dir = capture(exposure_time, 1.0, 1, wide_cam=wide_cam) # takes image and returns save path
        print(f"Image saved as: {image_dir}")  
        
        
        

        files.append(image_dir)
        image_file = image_dir+"/"
        # rsync_files(image_file, rsync_to)
        demosaic_image = True                                    
        files = [f"{image_dir}/{f}" for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
        #sorted(glob.glob(image_file))         # finds files in image dir 
        print(files[0])
        if demosaic_image == False : 
            image = hist.load_tiff(files[0]) 
        else : 
            image = demosaic(files[0])
            print("demosaiced image")
        ROI_array = hist.extract_ROI(image)
        tp.live_plot(ROI_array)

        red_pixels = ROI_array[:,:, 0].ravel()
        green_pixels = ROI_array[:,:, 1].ravel()
        blue_pixels = ROI_array[:,:, 2].ravel()

        stats["median_R"].append(np.median(red_pixels))
        stats["median_G"].append(np.median(green_pixels))
        stats["median_B"].append(np.median(blue_pixels))
        stats["irradiance"].append(irrad)

        deltamax_red = np.max(red_pixels) - np.min(red_pixels)
        deltamax_green = np.max(green_pixels) - np.min(green_pixels)
        deltamax_blue = np.max(blue_pixels) - np.min(blue_pixels)
        print(f"Deltamaxes: r({deltamax_red}), g({deltamax_green}), b({deltamax_blue})")


    print("Capture and sync complete")
    print(f"Stats dict: {stats}")
    live_analyse(stats)
    tp.plot_medians(stats)

#def local_analyse(image_path) :
def live_analyse(stats) :
    # if choose_dirs :
    #     csv_path = file_gui("OPM Log csv", is_dir=False)
    #     image_dir = file_gui("Image Directory", is_dir=True)
    # else :
    #     csv_path = "/home/thomas/Documents/Code/QuadStar/Calibration/OPM-Logs/0.5s_02.csv"      #"/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/plots/Calibrations/0.4s_clean.csv"#"/home/thomas/Pictures/Quadstar/Calibration/plots/0.3/585mm-0.3sTest_cleaned.csv"
    #     image_dir = "/home/thomas/Documents/Code/QuadStar/Calibration/plots/0.5/"
    #
    # exptime = image_dir.split("/")[-2]
    # print(f"Found image exposure time from directory name: {exptime}")
    # files_dict = combine_data(csv_path=csv_path, image_dir=image_dir)
    # stats = calc_stats(files_dict)

    exptime = stats["exp_time"]    

    x = stats["irradiance"]
    y_array = [stats["median_R"], stats["median_G"], stats["median_B"]]

    plt.scatter(x, stats["median_R"], color="red", label="Median R")
    plt.scatter(x, stats["median_G"], color="green", label="Median G")
    plt.scatter(x, stats["median_B"], color="blue", label="Median B")

    plt.xlabel("Irradiance (W/cm^2)")
    plt.ylabel("Median ADU")
    plt.title(f"Median ADU vs Irradiance with {exptime}s exposures")
    plt.legend()
    plt.savefig(f"/home/pi/QuadStar_Auxillary_Computer/Median_ADU_vs_Irradiance_{exptime}_{datetime.now()}.png")
    plt.show()

def analyse(choose_dirs=True): 
    if choose_dirs :
        csv_path = file_gui("OPM Log csv", is_dir=False)
        image_dir = file_gui("Image Directory", is_dir=True)
    else :
        csv_path = "/home/thomas/Documents/Code/QuadStar/Calibration/OPM-Logs/0.5s_02.csv"      #"/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/plots/Calibrations/0.4s_clean.csv"#"/home/thomas/Pictures/Quadstar/Calibration/plots/0.3/585mm-0.3sTest_cleaned.csv"
        image_dir = "/home/thomas/Documents/Code/QuadStar/Calibration/plots/0.5/"
    
    exptime = image_dir.split("/")[-2]
    print(f"Found image exposure time from directory name: {exptime}")
    files_dict = combine_data(csv_path=csv_path, image_dir=image_dir)
    stats = calc_stats(files_dict)



    x = stats["Irradiance (W/cm^2)"]
    y_array = [stats["Mean R"], stats["Mean G"], stats["Mean B"]]

    plt.scatter(x, stats["Mean R"], color="red", label="Mean R")
    plt.scatter(x, stats["Mean G"], color="green", label="Mean G")
    plt.scatter(x, stats["Mean B"], color="blue", label="Mean B")

    plt.xlabel("Irradiance (W/cm^2)")
    plt.ylabel("Mean ADU")
    plt.title(f"Mean ADU vs Irradiance with {exptime}s exposures")
    plt.legend()
    plt.savefig(f"/home/thomas/Documents/Code/QuadStar/Calibration/saved_plots/Mean_ADU_vs_Irradiance_{exptime}_{datetime.now()}.png")
    plt.show()


if __name__ == "__main__" :
    run = True
    try :
        mode = (sys.argv[1])     #int(input("Choose a mode:\n1: Capture\n2: Analyse\nSelection: "))
    except :
        print("Oosp! You didn't specify a mode. Do you are have stupid?")
        mode = input("Use '-c' for capture mode (run on the Pi)\nUse '-a' for analyse mode (run locally)\nMode: ")
        print("Next time put it in the command args, silly!")

    if mode == "-c" :
        print("======================\nCapture Mode")
        test_name = input("Test name: ")
        num_exposures = int(input("How many exposures?: "))
        exp_time = float(input("Enter exposure time (s): "))
        print(f"Default rsync save path: ~/Documents/Code/QuadStar/Calibration/")
        if input("Do you want to sync the image files to a different directory? (y/n)") == 'y' :
            rsync_dir = "192.168.0.164:/home/thomas/Documents/Code/QuadStar/" + input(f"Where? 192.168.0.164:~/Documents/Code/Quadstar/")
            print(f"Saving to: {rsync_dir}")
        else :
            rsync_dir = f"thomas@10.229.169.96:/home/thomas/Documents/Code/QuadStar/Calibration/Rsync-Images/{test_name}_exp{exp_time}_{datetime.now()}/"
        collect_data(exp_time, num_exposures, f"{exp_time}"+f"{datetime.now()}", wide_cam=False, demosaic_image=False, rsync_to=rsync_dir) # demosaic isn't needed here because it is done during analysis.
    elif mode == "-a" :
        print("======================\nAnalysis Mode")
        analyse()

    elif mode == "-s" :
        print("======================\nSetup Mode")
        exp_time = float(input("What exposure time are you using?: "))
        adjust_light_source(exposure_time=exp_time)


