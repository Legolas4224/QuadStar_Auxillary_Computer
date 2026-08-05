from camera import CameraLogic
import numpy as np
import time
import sys

def main():
	cam = CameraLogic(manual=True)
	print(f"{cam.supported_controls()}\n\n")
	exposure_values = [0.11, 0.25, 0.5, 1]		#s
	gain_values = [1.0]
	cam.collect_calibration_data(exposure_values, gain_values)
	cam.close()

def main_manual(exposure_length, gain, num_frames):
	cam = CameraLogic(manual=True)
	print(f"{cam.supported_controls()}\n\n")
	#cam.collect_calibration_data()
	print("\n================ Image Capture Running ==================")
	print(f"Exposure Time: {exposure_length}\nGain: {gain} \nFrames: {num_frames}\n")
	cam.run_exposures(exposure_length,gain,num_frames)
	cam.close()


if __name__ == "__main__":
	if sys.argv[1] :
		if sys.argv[1] == '-h' :
			print("exposure_length = float(sys.argv[1]) gain = float(sys.argv[2]) num_frames = int(sys.argv[3])")
		else :
			exposure_length = float(sys.argv[1])
			gain = float(sys.argv[2])
			num_frames = int(sys.argv[3])
			main_manual(exposure_length,gain,num_frames)
	else :
		main()
