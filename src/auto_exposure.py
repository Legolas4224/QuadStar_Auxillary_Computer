from camera import CameraLogic
import csv
import numpy as np

def calculate_exposure(test_vals):

    averages = {}
    for k, v in test_vals.items():
        averages[k] = np.mean(np.array(v))

    exp_lengths = list(averages.keys())
    brights = list(averages.values())

    coeffs = np.polyfit(brights, exp_lengths, 1)
    gradient, intercept = coeffs

    #
    AIM_BRIGHTNESS = 10000 # change this maybe (guess)
    MAX_EXPOSURE = 7 # 40 secs max for auto solver to utilize
    MIN_EXPOSURE = 0.005 # 1/200th of a sec
    #

    exposure = gradient * AIM_BRIGHTNESS + intercept
    exposure = round(exposure, 3)
    exposure = max(MIN_EXPOSURE, exposure)
    exposure = min(MAX_EXPOSURE, exposure)

    return exposure

 
def main():
    vals = {}
    with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv") as f:
        reader = csv.reader(f)
        print(reader)
        for row in reader:
            if float(row[0]) not in vals:
                vals[float(row[0])] = []
            vals[float(row[0])].append(float(row[1]))
        

    calculated_exposure = calculate_exposure(vals)
    NUM_FRAMES = 5

    cam = CameraLogic(manual=True)
    cam.run_exposures(calculated_exposure, 1.0, NUM_FRAMES)
    cam.close()


if __name__ == "__main__":
    main()
