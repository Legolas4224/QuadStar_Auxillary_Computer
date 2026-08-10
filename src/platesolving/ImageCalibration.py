import astropy
from astropy.stats import sigma_clip
import numpy as np
import glob

# GLOBAL PARAMS
raw_darks_path = "test_images/Darks/0.5s"
master_dark_output_path = "test_images/Darks/0.5s"
filetype = ".dng"

def load(raw_darks_path) :
    # ======== Load Images ==========
    files = sorted(glob.glob(f"{raw_image_path}*.{filetype}"))
    print(f"Found {len(files)} frames")

    if not files:
        raise RuntimeError("No image files found.")
    return files

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
    frames = load(raw_darks_path=raw_darks_path)
    master_dark = sigma_clipped_stack(frames, sigma=2.5)
    
    return master_dark

def dark_calibrate_lights(lights, master_dark) :
    calibrated_lights = []
    for light in lights :
        calibrated = light - master_dark
        calibrated_lights.append(calibrated)
    return calibrated_lights

if __name__ == "__main__" :
    master_dark = integrate_darks()
    