from camera import CameraLogic
import numpy as np
import time

def main():
	cam = CameraLogic(manual=True)
	print(f"{cam.supported_controls()}\n\n")
	#cam.collect_calibration_data()
	cam.run_exposures(0.5,1.0,5)
	cam.close()


if __name__ == "__main__":
	main()
