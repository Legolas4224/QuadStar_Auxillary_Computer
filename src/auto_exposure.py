from camera import CameraLogic
import csv
import numpy as np

def calculate_exposure(test_vals):
    max_pixel_value = 65520.0
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
    target_median.append((max_pixel_value - intercept) / gradient)

    averages = {}
    for k, t in test_vals.items():
        v, _, _ = t[0]
        averages[k] = np.mean(np.array(v))

    exp_lengths = list(averages.keys())
    brights = list(averages.values())

    coeffs = np.polyfit(brights, exp_lengths, 1)
    gradient, intercept = coeffs

    #
    AIM_BRIGHTNESS = np.mean(target_median) + 1000 # change this maybe (guess)
    MAX_EXPOSURE = 7 # 40 secs max for auto solver to utilize
    MIN_EXPOSURE = 0.00011 # Lowest value possible for Pi HQ camera
    #

    exposure = gradient * AIM_BRIGHTNESS + intercept
    exposure = round(exposure, 5)
    exposure = max(MIN_EXPOSURE, exposure)
    exposure = min(MAX_EXPOSURE, exposure)

    return exposure

 
def main():
    cam = CameraLogic(manual=True)

    # Scan across a range of exposures and gains
    exposure_values = [0.00011, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1] #s
    gain_values = [1.0]
    cam.collect_calibration_data(exposure_values, gain_values, 1)

    vals = {}
    with open("/home/pi/images/calibration_data/img_median.csv") as f:
        reader = csv.reader(f)
        print(reader)
        for row in reader:
            if float(row[0]) not in vals:
                vals[float(row[0])] = []
            vals[float(row[0])].append([float(row[1]), float(row[2]), float(row[3])])   
        
    calculated_exposure = calculate_exposure(vals)
    NUM_FRAMES = 5

    cam.run_exposures(calculated_exposure, 1.0, NUM_FRAMES)
    cam.close()


if __name__ == "__main__":
    main()
