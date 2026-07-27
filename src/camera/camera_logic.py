import sys
import tty
import termios
from picamera2 import Picamera2, Preview

class CameraLogic:
	def __init__(self, config=None):
		self.picam2 = Picamera2()
		self.config = config or  self.picam2.create_preview_configuration()
		self.picam2.configure(self.config)
		self.preview_started = False
		self.exposure = 4000
		self.gain = 3.0

	def start_preview(self, preview_type=Preview.DRM):
		self.picam2.start_preview(preview_type)
		self.preview_started = True
		self.picam2.start()

	def stop_preview(self):
		if self.preview_started:
			self.picam2.stop_preview()
		self.picam2.stop()

	def close(self):
		self.picam2.close()

	def supported_controls(self):
		return self.picam2.camera_controls

	def set_controls(self, exposure, gain):
		self.exposure = exposure
		self.gain = gain
		self.picam2.set_controls({"ExposureTime": self.exposure, "AnalogueGain": self.gain})

	def get_controls(self):
		return [self.exposure, self.gain]

