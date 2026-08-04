from picamera2 import Picamera2, Preview
import numpy as np
import time
import os
from datetime import datetime

class CameraLogic:
	#Initialise camera
	def __init__(self, manual=False, config=None):
		self.picam2 = Picamera2()
		#This configuration is for previewing the camera
		self.preview_config = self.picam2.create_preview_configuration()
		#This configuration is for taking images
		self.still_config = self.picam2.create_still_configuration(
			raw={"format": "SRGGB12", "size": (4056, 3040)},
			sensor={"output_size": (4056, 3040), "bit_depth": 12},
			controls={"FrameDurationLimits": (110,900000)},
		)
		self.picam2.configure(self.preview_config)
		self.preview_started = False

	#Start camera
	def start(self):
		self.picam2.start()

	#Stop and close camera
	def close(self):
		self.picam2.stop()
		self.picam2.close()

	#Display camera view
	def start_preview(self, preview_type=Preview.DRM):
		self.picam2.start_preview(preview_type)
		self.preview_started = True
		self.picam2.start()

	#Stop camera preview
	def stop_preview(self):
		if self.preview_started:
			self.picam2.stop_preview()

	#Return the camera parameters for calibrating
	def supported_controls(self):
		print(self.picam2.camera_controls)

	#Set the camera exposure time and gain values
	def set_brightness(self, exposure, gain):
		self.picam2.set_controls({"ExposureTime": exposure, "AnalogueGain": gain})

	#Get the camera metadata
	def get_metadata(self):
		return self.picam2.capture_metadata()

	#Capture the current image
	#Return an array with RGB channels
	def capture_rgb(self):
		return self.picam2.capture_array()[:,:,:3]

	def run_exposures(self, exposure_seconds, gain, num_exposures):
			self.picam2.configure(self.still_config)
			self.start()
			self.picam2.set_controls({"AeEnable": False})
			gain_value = gain  # [1.0, 2.0, 4.0]
			#exposure_values = [250,500,1000]   # [0.11, 0.5, 1, 5, 10, 50, 100, 500, 1000]	#ms
			#exposure_values = [ex * 10**3 for ex in exposure_values]
			exposure_value = exposure_seconds * 10**6


			
			self.set_brightness(int(exposure_value), gain_value)

			capture_dir = f"/mnt/images/QuadStar/{datetime.now():%Y%m%d_%H%M%S}_e-{exposure_seconds}_g-{gain}_n-{num_exposures}"
			os.makedirs(capture_dir, exist_ok=True)

			#Loop until camera updates new settings
			timeout = time.time() + 2.0
			metadata = self.get_metadata()
			while time.time() < timeout:
				metadata = self.get_metadata()
				if (abs(metadata["ExposureTime"] - exposure_value) < 100) and (abs(metadata["AnalogueGain"] - gain_value) < 0.1):
					break

			#Save raw image to file
			for _ in range(num_exposures):
				request = self.picam2.capture_request()
				request.save_dng(f"{capture_dir}/Ex{metadata['ExposureTime']}_({exposure_seconds}s)_Gain{metadata['AnalogueGain']}_Temp{metadata['SensorTemperature']}_{time.time()}.dng")
				request.release()
				print(f"Took picture at: Ex:{metadata['ExposureTime']} Gain:{metadata['AnalogueGain']} Temp:{metadata['SensorTemperature']} {time.time()}")

		
	def collect_calibration_data(self):
		self.picam2.configure(self.still_config)
		self.start()
		self.picam2.set_controls({"AeEnable": False})
		gain_values = [1.0]  # [1.0, 2.0, 4.0]
		exposure_values = [250,500,1000]   # [0.11, 0.5, 1, 5, 10, 50, 100, 500, 1000]	#ms
		exposure_values = [ex * 10**3 for ex in exposure_values]

		for exposure in exposure_values:
			for gain in gain_values:
				self.set_brightness(int(exposure), gain)

				#Loop until camera updates new settings
				timeout = time.time() + 2.0
				metadata = self.get_metadata()
				while time.time() < timeout:
					metadata = self.get_metadata()
					if (abs(metadata["ExposureTime"] - exposure) < 100) and (abs(metadata["AnalogueGain"] - gain) < 0.1):
						break

				#Save raw image to file
				for _ in range(2):
					request = self.picam2.capture_request()
					request.save_dng(f"./data/Ex:{metadata['ExposureTime']}_Gain:{metadata['AnalogueGain']}_Temp:{metadata['SensorTemperature']}_{time.time()}.dng")
					request.release()
					print(f"Took picture at: Ex:{metadata['ExposureTime']} Gain:{metadata['AnalogueGain']} Temp:{metadata['SensorTemperature']} {time.time()}")


	#Simple function to find the exposure time and gain to reach the target brightness
	#Notes: This works but it converges to the target brightness very slowly, especially if it is overexposed.
	#Next steps: - Try a calibration function, sweep through a range of exposure and gain to quickly get the correct setting
	#            - Or find a math function that converges faster
	#			 - Try a different method of auto exposure
	def auto_exposure(self, current, target, plate_solving):
		min_exposure, max_exposure = 1000, 1000000
		min_gain, max_gain = 1.0, 16.0

		frame = self.capture()
		metadata = self.get_metadata()
		exposure, gain = metadata["ExposureTime"], metadata["AnalogueGain"]

		if plate_solving:
			while current != target:
				scale = target / current
				if gain < max_gain:
					gain *= scale
				elif exposure < max_exposure:
					exposure *= scale
				gain = max_gain if gain > max_gain else gain
				exposure = max_exposure if exposure > max_exposure else exposure

				self.set_brightness(int(exposure), gain)
				for _ in range(5):
					self.capture()

				print(f"Exposure: {exposure}, Gain: {gain}, Brightness: {current}")

				frame = self.capture()
				current = np.percentile(frame, 99)

	def ae_plate_solving_mode(self):
		self.picam2.set_controls({"AeEnable": False})

		#This set controls is just for testing the mode
		self.set_brightness(1000, 1.0)
		for _ in range(5):
			self.capture()

		target_brightness = 253

		print(self.get_metadat())

		while True:
			frame = self.capture()
			current_brightness = np.percentile(frame, 99)
			if current_brightness != target_brightness:
				self.auto_exposure(current_brightness, target_brightness, plate_solving=True)

