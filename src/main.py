from camera import CameraLogic
import numpy as np
import time
import sys

def main():
	cam = CameraLogic(manual=True)
	print(f"{cam.supported_controls()}\n\n")
	#cam.collect_calibration_data()
	cam.run_exposures(0.5,1.0,20)
	cam.close()

def main_manual(exposure_length, gain, num_frames):
	cam = CameraLogic(manual=True)
	print(f"{cam.supported_controls()}\n\n")
	#cam.collect_calibration_data()
	cam.run_exposures(exposure_length,gain,num_frames)
	cam.close()


if __name__ == "__main__":
	if sys.argv[1] :
		if sys.argv[1] == '-h' :
			print("exposure_length = int(sys.argv[1]) gain = int(sys.argv[2]) num_frames = int(sys.argv[3])")
		else :
			exposure_length = int(sys.argv[1])
			gain = int(sys.argv[2])
			num_frames = int(sys.argv[3])
			main_manual(exposure_length,gain,num_frames)
	else :
		main()
