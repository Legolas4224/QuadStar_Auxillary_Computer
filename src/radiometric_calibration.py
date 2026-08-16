import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from pprint import pprint
from histogram import load_tiff, plot_histogram
from datetime import datetime, timedelta

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
    #print(files_dict)
    image_list = []
    median_list = []
    irradiance_list = []
    mean_list = []
    mean_list_R = []
    mean_list_G = []
    mean_list_B = []

    for entry in files_dict.values() :
        image = entry[1]
        #print(image)
        image = demosaic(image)
        #print(np.shape(image))
        #plot_histogram(image, "debayertest", ROI=False)
        #image = load_tiff(image)
        img_array = image
        #print("Mean: ", np.mean(img_array))
        #print("Median: ", np.median(img_array))
        #print("Max: ", np.max(img_array))
        #print("Min: ", np.min(img_array))
        median = np.median(img_array)
        mean = np.mean(img_array)
        R_mean, G_mean, B_mean = np.mean(img_array, axis=(0,1))
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
            median_list.append(median)
            irradiance_list.append(irradiance)
            mean_list.append(mean)
            mean_list_R.append(R_mean)
            mean_list_G.append(G_mean)
            mean_list_B.append(B_mean)
    
    stats_dict = {
        #"image" : image_list,
        #"Median ADU" : median_list,
        "Mean R" : mean_list_R,
        "Mean G" : mean_list_G,
        "Mean B" : mean_list_B,
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


#demosaic("/home/thomas/Documents/Code/QuadStar/Calibration/plots/0.5/Image-Mean27970.8592_ROI(100, 100)_0.5_12-8-15:58:52.tiff", "/home/thomas/Documents/Code/QuadStar/Calibration/DebayerTest/test.tiff")

def main(choose_dirs=True) :
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

    #stats.plot(y="Mean R", x="Irradiance (W/cm^2)", kind="scatter")
    #stats.plot(y="Mean G", x="Irradiance (W/cm^2)", kind="scatter")
    #stats.plot(y="Mean B", x="Irradiance (W/cm^2)", kind="scatter")
    #title = f"Mean ADU vs Irradiance with 1s exposures-{datetime.now()}"
    #plt.title(title)
    #plt.savefig(f"/home/thomas/Documents/Code/QuadStar/Calibration/saved_plots/{title}.png")
    #plt.show()

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
    main()



