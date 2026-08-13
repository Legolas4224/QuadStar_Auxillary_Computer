from camera import CameraLogic
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def calculate_exposure(test_vals):
    max_pixel_value = 65520
    num_pixels = 4056 * 3040
    target_median = []
    median_values = []
    max_values = []
    for ex, t in test_vals.items():
        median, max_value, count = t[0]
        if max_value == max_pixel_value and 0 < count and count < num_pixels * 0.1:
            target_median.append(median)
        elif max_value < max_pixel_value:
            median_values.append(median)
            max_values.append(max_value)
    
    coeffs = np.polyfit(np.array(median_values), np.array(max_values), 1)
    gradient, intercept = coeffs
    target = (max_pixel_value - intercept) / gradient
    target_median.append(target + target * 0.1)

    averages = {}
    for k, t in test_vals.items():
        v, _, _ = t[0]
        averages[k] = np.mean(np.array(v))

    exp_lengths = list(averages.keys())
    brights = list(averages.values())

    coeffs = np.polyfit(brights, exp_lengths, 1)
    gradient, intercept = coeffs

    #
    AIM_BRIGHTNESS = 10000 # change this maybe (guess)
    MAX_EXPOSURE = 10 # 50 secs max for auto solver to utilize
    MIN_EXPOSURE = 0.005 # 1/200th of a sec
    #

    exposure = gradient * AIM_BRIGHTNESS + intercept
    exposure = round(exposure, 5)
    exposure = max(MIN_EXPOSURE, exposure)
    exposure = min(MAX_EXPOSURE, exposure)

    print(f"\n\nTargets: {target_median}, Aim brightness: {AIM_BRIGHTNESS}, new exposure: {exposure}\n\n")
    # FOR TESTING
    # exposure = MAX_EXPOSURE 

    return exposure

 
def main():
 
    # Scan across a range of exposures and gains
    #exposure_values = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1] #s
    #for exposure in exposure_values:    
    #   cam.run_exposures(exposure, 1.0, 1)
    # Removed as we just use our actual exposures for this

    vals = {}
    with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv") as f:
        reader = csv.reader(f)
        print(reader)
        for row in reader:
            if float(row[0]) not in vals:
                vals[float(row[0])] = []
            try:
                vals[float(row[0])].append([float(row[1]), float(row[2]), float(row[3])])
            except:
                pass
        
    calculated_exposure = calculate_exposure(vals)
    NUM_FRAMES = 5

    cam = CameraLogic(manual=True, exposure=calculated_exposure)
    cam.run_exposures(calculated_exposure, 1.0, NUM_FRAMES)
    cam.close()

if __name__ == "__main__":
    main()
