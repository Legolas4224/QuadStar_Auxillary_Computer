from camera import CameraLogic
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def calculate_exposure(test_vals):
    max_pixel_value = 65472
    num_pixels = 4608 * 2592    #4056 * 3040
    values_95 = []
    exposure_values = []
    overexpose_count = []
    overexposure_values = []

    #
    AIM_BRIGHTNESS = max_pixel_value # change this maybe (guess)
    MAX_EXPOSURE = 10 # 50 secs max for auto solver to utilize
    MIN_EXPOSURE = 0.005 # 1/200th of a sec
    #
    target = None

    for ex, t in test_vals.items():
        median, value_95, max_value, count = t[0]
        if max_value == max_pixel_value and count > num_pixels * 0.1 and count < num_pixels * 0.6:
            overexpose_count.append(count)
            overexposure_values.append(ex)
        elif max_value <= max_pixel_value and count < num_pixels * 0.1:
            values_95.append(value_95)
            exposure_values.append(ex)

    if  len(values_95) > len(overexpose_count):
        print("Underexposed. Increasing brightness\n\n")
        coeffs = np.polyfit(np.array(exposure_values), np.array(values_95), 1)
        gradient, intercept = coeffs

        '''averages = {}
        for k, t in test_vals.items():
            v, _, _, _ = t[0]
            averages[k] = np.mean(np.array(v))

        exp_lengths = list(averages.keys())
        brights = list(averages.values())

        coeffs = np.polyfit(brights, exp_lengths, 1)
        gradient, intercept = coeffs    
        '''

        exposure = (AIM_BRIGHTNESS - intercept) / gradient
        exposure = round(exposure, 5)
        target = max_pixel_value
    else: 
        print("Overexposed. Recalculating\n\n")
        # Handle overexposure
        coeffs = np.polyfit(np.array(overexposure_values), np.array(overexpose_count), 1)
        gradient, intercept = coeffs

        aim_count = 0.07 * num_pixels
        exposure = (aim_count - intercept) / gradient
        exposure = round(exposure, 5)
        target = aim_count

    exposure = max(MIN_EXPOSURE, exposure)
    exposure = min(MAX_EXPOSURE, exposure)

    print(f"\n\nTargets: {target}, Aim brightness: {AIM_BRIGHTNESS}, new exposure: {exposure}\n\n")
    # FOR TESTING
    # exposure = MAX_EXPOSURE 

    return exposure

 
def main():

    vals = {}
    with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv") as f:
        reader = csv.reader(f)
        print(reader)
        for row in reader:
            if float(row[0]) not in vals:
                vals[float(row[0])] = []
            try:
                vals[float(row[0])].append([float(row[1]), float(row[2]), float(row[3]), float(row[4])])
            except:
                pass
        
    calculated_exposure = calculate_exposure(vals)
    NUM_FRAMES = 5

    cam = CameraLogic(manual=True, exposure=calculated_exposure)
    cam.run_exposures(calculated_exposure, 1.0, NUM_FRAMES)
    cam.close()

if __name__ == "__main__":
    main()
