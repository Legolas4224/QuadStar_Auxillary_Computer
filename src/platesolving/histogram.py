from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

def plot_histogram(image_path) :

    image = fits.getdata(image_path)

    plt.hist(image.ravel(), bins=1000)
    plt.xlabel("Pixel value")
    plt.ylabel("Number of pixels")
    plt.title("Image Histogram")
    plt.show()

#plot_histogram("/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/QuadStar/20260807_183141_e-0.5_g-1.0_n-5.done/2026-08-07 08:31:44.825588+00:00.fits")
plot_histogram("/home/thomas/Pictures/M_8/Light_M_8_010.fits")