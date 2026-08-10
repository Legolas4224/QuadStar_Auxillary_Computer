import numpy as np
import csv
import matplotlib.pyplot as plt
from main import main_manual as capture

# goal: plot image stats vs exposure time
# find absolute sensor response to light power
# calibrate images - darks and flats


# GLOBAL PARAMS
raw_path = "/home/pi/QuadStar_Auxillary_Computer/data/"     #"test_images/Darks/0.5s"
#master_dark_output_path = "test_images/Darks/0.5s"
filetype = ".dng"

def load(raw_path) :
    # ======== Load Images ==========
    files = sorted(glob.glob(f"{raw_path}*.{filetype}"))
    print(f"Found {len(files)} frames")

    if not files:
        raise RuntimeError("No image files found.")
    return files


exp_time = 0.5

capture(exp_time, 1.0, 10)
images = load(raw_path)
clipped = sigma_clip(images, sigma=sigma, axis=0, maxiters=3)
# Mean of non-rejected values at each pixel position
stacked = np.ma.mean(clipped, axis=0).data


light_power = input("Enter light power: ")


