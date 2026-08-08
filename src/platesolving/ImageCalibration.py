import astropy
from astropy.io import fits
from astropy.stats import sigma_clip
import numpy as np
import glob
from format_converter import convert_dng_to_fits
from datetime import datetime, timezone
import os

# GLOBAL PARAMS
raw_darks_path = "/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/CalibrationTesting/Darks/0.5s/"
master_dark_output_path = "/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/CalibrationTesting/Darks"
filetype = "dng"


def load(raw_image_path, fits_dir=None) :
    # ======== Load Images ==========
    files = sorted(glob.glob(f"{raw_image_path}*.{filetype}"))
    print(f"Found {len(files)} frames")

    if not files:
        raise RuntimeError("No image files found.")
    
    now = datetime.now()

    # fix
    if fits_dir is None:
        fits_dir = f"{raw_image_path}-{now}-fits/"
    else:
        fits_dir = fits_dir + f"-{now}-fits/"

    os.mkdir(fits_dir)
    converted_files = []
    i = 0
    timestamps = []
    if filetype == "dng":
        for file in files:
            i += 1
            newname = f"{file.removesuffix('.dng')}".split("/")[-1]
            converted = convert_dng_to_fits(file, f"{fits_dir}/{newname}.fits")
            converted_files.append(converted)
            timestamps.append(f"{newname}".split("_")[-1])
    elif filetype == "tiff":
        for file in files:
            i += 1
            # temp fix
            # newname = f"{file.removesuffix('.tiff')}".split("/")[-1]
            newname = f"{file.removesuffix('.tiff')}".split("_17")[-1]
            converted = tiff_to_fits(file, f"{fits_dir}/{newname}.fits")
            converted_files.append(converted)
            timestamps.append("17" + f"{newname}".split("_17")[-1])

    return converted_files

def sigma_clipped_stack(frames, sigma=2.5):

        print(f"Integrating Frames")
        """
        Stack frames using sigma-clipped mean.
        Each pixel position is evaluated independently across all frames.
        """
        # sigma_clip returns a masked array — rejected values are masked out
        clipped = sigma_clip(frames, sigma=sigma, axis=0, maxiters=3)
        # Mean of non-rejected values at each pixel position
        stacked = np.ma.mean(clipped, axis=0).data
        return stacked

def integrate_darks() :
    frames = load(raw_darks_path)
    images = []
    for frame in frames :
        image = fits.getdata(frame)
        images.append(image)
    stack = np.stack(images)
    master_dark = sigma_clipped_stack(stack, sigma=2.5)
    output_path = f"{master_dark_output_path}/{datetime.now()}.fits"
    #os.mkdir(master_dark_output_path)
    fits.writeto("/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/IntegratedDarks/dark.fits", master_dark, overwrite=True)
    print(f"Integration Complete: Image saved as {output_path}")
    
    return master_dark

def dark_calibrate_light(light) :
    master_dark = fits.getdata("/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/IntegratedDarks/dark.fits").astype(np.float32)
    return (light - master_dark)
    #calibrated_lights = []

    #for light in lights :
    #    calibrated = light - master_dark
    #    calibrated_lights.append(calibrated)
    #return calibrated_lights

if __name__ == "__main__" :
    master_dark = integrate_darks()
