import plotext as plt
import numpy as np
from PIL import Image

#def plot(x, y) :
#    plt.title("Histogram")
#    y = plt.
#

def live_plot(img_array) :

    plt.clear_figure()
    #hist, bin_edges = np.histogram(
    #img_array.ravel(),
    #bins=200,
    #range=(0, 65535)
    #)

    #bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2

    #plt.plot(bin_centres, hist)
    #plt.show()

    #plt.plot(x, temperature, label="Temperature", color='blue')
    #plt.plot(x, pressure, label="Pressure", color='red')

   

    hist_r, bins = np.histogram(img_array[:, :, 0].ravel(), bins=100, range=(0, 65535))
    hist_g, _    = np.histogram(img_array[:, :, 1].ravel(), bins=100, range=(0, 65535))
    hist_b, _    = np.histogram(img_array[:, :, 2].ravel(), bins=100, range=(0, 65535))

    centres = (bins[:-1] + bins[1:]) / 2

    plt.plot(centres, hist_r, color="red", label="R")
    plt.plot(centres, hist_g, color="green", label="G")
    plt.plot(centres, hist_b, color="blue", label="B")

    plt.theme('matrix')

    plt.clear_terminal()
    plt.title("Sensor data")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.show()

def view_image(img):

    plt.clear_figure()
    img.save("./_temp.png")
    plt.image_plot("./_temp.png")
    plt.show()

    
    
