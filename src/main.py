from camera import CameraLogic
import numpy as np
import time

def main():
	cam = CameraLogic(manual=True)
	cam.start_preview()
	time.sleep(1)
	cam.ae_plate_solving_mode()
	input()
	cam.stop_preview()
	cam.close()


if __name__ == "__main__":
	main()
