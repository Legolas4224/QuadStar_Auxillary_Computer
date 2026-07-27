from camera import CameraLogic
import sys
import tty
import termios

def get_key():
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	try:
		tty.setraw(fd)
		key = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)
	return key

def main():
	cam = CameraLogic()
	exposure, gain = cam.get_controls()

	cam.start_preview()

	while True:
		key = get_key()
		if key == "-":
			gain -= 0.1
			print("Gain:", gain)
		elif key == "=":
			gain += 0.1
			print("Gain:", gain)
		elif key == "[":
			exposure -= 100
			print("Exposure:", exposure)
		elif key == "]":
			exposure += 100
			print("Exposure:", exposure)
		elif key == "q":
			break
		cam.set_controls(exposure, gain)

	cam.stop_preview()
	cam.close()

if __name__ == "__main__":
	main()
