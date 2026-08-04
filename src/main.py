from camera import CameraLogic
import numpy as np
import time

def main():
	cam = CameraLogic(manual=True)
	print(f"{cam.supported_controls()}\n\n")
	cam.collect_calibration_data()
	cam.close()


if __name__ == "__main__":
	main()
