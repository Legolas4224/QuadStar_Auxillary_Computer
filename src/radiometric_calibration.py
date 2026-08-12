import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from pprint import pprint
from histogram import load_tiff

def combine_data(csv_path, image_dir) : # This looks through all the images and finds the closest datapoint from the csv. It then makes a dictionary with all the relevant info

    df = pd.read_csv(csv_path)
    df["time"] = pd.to_timedelta(df["Time of day (hh:mm:ss) "])
    print(df)
    
    files = sorted(glob.glob(f"{image_dir}/*.tiff"))
    print(f"{len(files)}")
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
            print(f"Found closest match for image {file}:")#\n{row}\n--------")
            
            power = row["Power (W)"]
            irradiance = row["Irradiance (W/cm²)"]
            power_dbm = row["Power (dBm)"]

            roi_file = file.replace("_full", "")



            files_dict[time] = [file, roi_file, power, irradiance, power_dbm]
    pprint(files_dict)
    return files_dict


def calc_stats(files_dict) :
    #print(files_dict)
    image_list = []
    median_list = []
    irradiance_list = []


    for entry in files_dict.values() :
        image = entry[1]
        print(image)
        image = load_tiff(image)
        img_array = image
        print("Mean: ", np.mean(img_array))
        print("Median: ", np.median(img_array))
        print("Max: ", np.max(img_array))
        print("Min: ", np.min(img_array))
        median = np.median(img_array)
        irradiance = entry[3]
        if irradiance == np.inf :
            pass
        elif irradiance == 0 :
            pass
        else :
            image_list.append(image)
            median_list.append(median)
            irradiance_list.append(irradiance)

    stats_dict = {
        #"image" : image_list,
        "Median ADU" : median_list,
        "Irradiance (W/m^2)" : irradiance_list
    }

    
    stats_df = pd.DataFrame(stats_dict)
    print(stats_df)
    return stats_df




csv_path = "/home/thomas/Pictures/Quadstar/Calibration/plots/0.3/585mm-0.3sTest_cleaned.csv"
image_dir = "/home/thomas/Pictures/Quadstar/Calibration/plots/0.3"

files_dict = combine_data(csv_path=csv_path, image_dir=image_dir)
stats = calc_stats(files_dict)

stats.plot(y="Median ADU", x="Irradiance (W/cm^2)", kind="scatter")
plt.title("Median ADU vs Irradiance with 0.3s exposures")
plt.savefig("plots/Median_vs_Irradiance.png")
plt.show()