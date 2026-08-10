from picamera2 import Picamera2, Preview
import numpy as np
import time
import os
import subprocess
from datetime import datetime
from tifffile import imwrite
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import csv

class CameraLogic:
    # Initialise camera
    def __init__(self, manual=False, config=None):
        try:
            self.picam2 = Picamera2()
        except IndexError as idx_err:
            subprocess.run(["vcgencmd", "get_camera"])
            self.picam2 = Picamera2()

        # This configuration is for previewing the camera
        self.preview_config = self.picam2.create_preview_configuration()
        # This configuration is for taking images
        self.still_config = self.picam2.create_still_configuration(
            raw={"format": "SRGGB12", "size": (4056, 3040)},
            sensor={"output_size": (4056, 3040), "bit_depth": 12},
            controls={"FrameDurationLimits": (110, 600000000), "AeEnable": False},
        )
		self.noIR_config = self.picam2.create_still_configuration(
			raw={"format": 'SRGGB10', "size": (4608, 2592)},
			sensor={"output_size": (4608, 2592), "bit_depth": 10},
			controls={"FrameDurationLimits": (110, 600000000), "AeEnable": False}
		)
		if Picamera2.global_camera_info()[0]["Model"] == 'imx708_wide_noir':
			self.picam2.configure(self.noIR_config)
		else:
	        self.picam2.configure(self.preview_config)
        self.preview_started = False

    # Start camera
    def start(self):
        self.picam2.start()

    # Stop and close camera
    def close(self):
        self.picam2.stop()
        self.picam2.close()

    # Display camera view
    def start_preview(self, preview_type=Preview.DRM):
        self.picam2.start_preview(preview_type)
        self.preview_started = True
        self.picam2.start()

    # Stop camera preview
    def stop_preview(self):
        if self.preview_started:
            self.picam2.stop_preview()

    # Return the camera parameters for calibrating
    def supported_controls(self):
        print(self.picam2.camera_controls)

    # Set the camera exposure time and gain values
    def set_brightness(self, exposure, gain):
        self.picam2.set_controls({"ExposureTime": exposure, "AnalogueGain": gain})

    # Get the camera metadata
    def get_metadata(self):
        return self.picam2.capture_metadata()

    # Capture the current image
    # Return an array with RGB channels
    def capture_rgb(self):
        return self.picam2.capture_array()[:, :, :3]

	def get_sensor_formats(self):
		for mode in self.picam2.sensor_modes:
			print(mode)

	#Capture {num_exposure} images at {exposure_seconds} and {gain}
	#Save as .dng file
	def run_exposures(self, exposure_seconds, gain, num_exposures):
		try:
			self.picam2.configure(self.still_config)
			self.start()
		except:
			None

		capture_dir = f"/home/pi/images/QuadStar/{datetime.now():%Y%m%d_%H%M%S}_e-{exposure_seconds}_g-{gain}_n-{num_exposures}"
		os.makedirs(capture_dir, exist_ok=True)

		exposure_value = exposure_seconds * 10**6
		self.set_brightness(int(exposure_value), gain)

        # Loop until camera updates new settings
        timeout = time.time() + 2.0
        metadata = self.get_metadata()
        while time.time() < timeout:
            metadata = self.get_metadata()
            if (abs(metadata["ExposureTime"] - exposure_value) < 100) and (
                abs(metadata["AnalogueGain"] - gain_value) < 0.1
            ):
                break
		#Loop until camera updates new settings
		timeout = time.time() + 2.0
		metadata = self.get_metadata()
		while time.time() < timeout:
			metadata = self.get_metadata()
			if (abs(metadata["ExposureTime"] - exposure_value) < 100) and (abs(metadata["AnalogueGain"] - gain) < 0.1):
				break

		#Save raw image to file
		for n in range(num_exposures):
			request = self.picam2.capture_request()
			img_filepath = f"{capture_dir}/e-{metadata['ExposureTime']}({exposure_seconds}s)_g{metadata['AnalogueGain']}_Temp{metadata['SensorTemperature']}_{n}.tiff"
			img_array = request.make_array(name="raw").view(np.uint16)
			imwrite(img_filepath, img_array)
			print(f"array info. flags({img_array.flags}), shape({img_array.shape}), size({img_array.size}), itemsize({img_array.itemsize}), nbytes({img_array.nbytes})")
			request.release()
			print(f"Took picture at: Ex:{metadata['ExposureTime']} Gain:{metadata['AnalogueGain']} Temp:{metadata['SensorTemperature']} {time.time()}")
            median = np.median(img_array)
            with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([exposure_seconds, median])	

	#Function to take images at a range exposure and gain values
	def collect_calibration_data(self, exposure_values, gain_values, num_exposures):
		for exposure in exposure_values:
			for gain in gain_values:
				self.run_exposures(exposure, gain, num_exposures)
