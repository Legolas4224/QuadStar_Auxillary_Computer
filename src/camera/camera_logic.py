from picamera2 import Picamera2, Preview
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

class CameraLogic:
	#Initialise camera
	def __init__(self, manual=False, config=None):
		self.picam2 = Picamera2()
		self.preview_config = self.picam2.create_preview_configuration()
		self.still_config = self.picam2.create_still_configuration()
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
	def capture(self):
		return self.picam2.capture_array()[:,:,:3]

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

		while True:
			frame = self.capture()
			current_brightness = np.percentile(frame, 99)
			if current_brightness != target_brightness:
				self.exposure_product(current_brightness, target_brightness, plate_solving=True)

