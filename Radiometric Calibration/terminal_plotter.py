import plotext as plt
import numpy as np

#def plot(x, y) :
#    plt.title("Histogram")
#    y = plt.
#

def live_plot(img_array) :


    hist, bin_edges = np.histogram(
    img_array.ravel(),
    bins=200,
    range=(0, 65535)
    )

    bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2

    plt.plot(bin_centres, hist)
    plt.show()

    #plt.plot(x, temperature, label="Temperature", color='blue')
    #plt.plot(x, pressure, label="Pressure", color='red')

    plt.theme('matrix')


    plt.title("Sensor data")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.show()