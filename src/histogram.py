from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import rawpy
from datetime import datetime
from main import main_manual as capture

def load_tiff(path) :
    from PIL import Image

    # Open the TIFF image
    image = Image.open(path)

    # Display basic properties
    print(f"Format: {image.format}, Size: {image.size}, Mode: {image.mode}")

    # Show the image
    #image.show()
    return image

def load_dng(path) :
    # Load the DNG image
    with rawpy.imread(path) as raw:
        # Postprocess converts raw data into a usable RGB numpy array
        rgb = raw.postprocess(use_camera_wb=True)

    # Convert the array into a standard PIL Image object
    image = Image.fromarray(rgb)

    # Show the image on screen
    image.show()

    # Optional: Save it as a standard format
    #image.save("output.jpg", "JPEG", quality=90)

def load_raw(path) :
    with rawpy.imread("/home/thomas/Documents/Code/QuadStar/Images/dng/100826/20260810_184516_e-0.5s_g-1.0_n-10.done/wide_2_1786351517.dng") as raw:
        # Access the raw 2D bayer array from the sensor
        raw_data = raw.raw_image

        print("Image dimensions:", raw_data.shape)

def plot_histogram(img, plotname, xlog=False, ylog=False, clip=False) :
    #image = fits.getdata(image_path)
    img_array = np.array(img)

    print("Mean: ", np.mean(img_array))
    print("Median: ", np.median(img_array))
    print("Max: ", np.max(img_array))
    print("Min: ", np.min(img_array))

    # 4. Calculate the 95th percentile
    #    This flattens the array and finds the value where 95% of pixels are below it
    brightness_threshold = np.percentile(img_array, 99)
    print("99% of pixels below: ", brightness_threshold)

    clip = False

    if clip:

        # Find actual min and max values present in your data
        data_min = np.min(img_array)
        data_max = np.max(img_array)

        # Plot only between the active range
        plt.hist(img_array.ravel(), bins=4000, range=(data_min, data_max), color="gray")
        plt.xlim(data_min, data_max)  # Forces the window to zoom in tight

    plt.hist(img_array.ravel(), bins=4000, range=(0, 65535), color="blue")

    plt.title("Histogram")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    if xlog :
        plt.xscale("log")
    if ylog :
        plt.yscale("log")
    

    # 3. Display the plot
    plt.tight_layout()
    now = datetime.now()
    import os
    os.makedirs("plots", exist_ok=True)
    plot_path = f"plots/Image-{plotname}_{now.day}-{now.month}-{now.hour}:{now.minute}:{now.second}",
    plt.savefig(plot_path+".png")
    return plot_path
    
    #plt.hist(image.ravel(), bins=1000)
    #plt.xlabel("Pixel value")
    #plt.ylabel("Number of pixels")
    #plt.title("Image Histogram")
    #plt.show()

def capture_to_histo(exptime) :
    import glob
    image_path = capture(exptime, 1.0, 1)
    files = sorted(glob.glob(f"{image_path}/*"))
    image = load_tiff(files[0])
    plot_path = plot_histogram(image, exptime, xlog=False, ylog=False)
    import shutil
    shutil.copy(image_path, plot_path+".tiff")
    print("Image file and histogram copied to plots dir")


def main(exp) :
    path = "/home/thomas/Documents/Code/QuadStar/Images/20260810_183233_e-30.0_g-1.0_n-5.solve/Ex6999327_(30.0s)_Gain1.0_Temp13.0_1786350760.9048686.tiff"


    #exp = float(input("Exp time (s): "))
    if exp == 0.5 :
        path = "/home/thomas/Documents/Code/QuadStar/Images/20260810_182334_e-0.5_g-1.0_n-5.solve/Ex499991_(0.5s)_Gain1.0_Temp14.0_1786350217.5650754.tiff"
    elif exp == 3 :
        path = "/home/thomas/Documents/Code/QuadStar/Images/20260810_182428_e-3.0_g-1.0_n-5.solve/Ex2999948_(3.0s)_Gain1.0_Temp15.0_1786350271.9747188.tiff"
    elif exp == 30 :
        path = "/home/thomas/Documents/Code/QuadStar/Images/20260810_183233_e-30.0_g-1.0_n-5.solve/Ex6999327_(30.0s)_Gain1.0_Temp13.0_1786350760.9048686.tiff"
    elif exp == 1 :
        path = "/home/thomas/Documents/Code/QuadStar/Images/ceiling_tiffs/Ex999982_(1.0s)_Gain1.0_Temp15.0_1785924314.6876094.tiff"

    print("loading image of exp time:", exp, "s")

    image = load_tiff(path)

    plotname = "30s"
    plot_histogram(image, plotname)

if __name__ == "__main__" :
    #main(30)
    import sys
    exp = float(sys.argv[1])
    capture_to_histo(exp)
