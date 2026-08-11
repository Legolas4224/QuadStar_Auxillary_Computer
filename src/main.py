#!/usr/bin/python3

from camera import CameraLogic
import sys


def main():
    cam = CameraLogic(manual=True)
    print(f"{cam.supported_controls()}\n\n")
    # cam.collect_calibration_data()
    cam.run_exposures(0.5, 1.0, 20)
    cam.close()


def main_manual(exposure_length, gain, num_frames):
    cam = CameraLogic(manual=True, exposure=exposure_length)
    print(f"{cam.supported_controls()}\n\n")
    # cam.collect_calibration_data()
    print("\n================ Image Capture Running ==================")
    print(f"Exposure Time: {exposure_length}\nGain: {gain} \nFrames: {num_frames}\n")
    output_dir = cam.run_exposures(exposure_length, gain, num_frames)
    cam.close()
    return output_dir

if __name__ == "__main__":
    if sys.argv[1]:
        if sys.argv[1] == "-h":
            print(
                "exposure_length = float(sys.argv[1]) gain = float(sys.argv[2]) num_frames = int(sys.argv[3])"
            )
        else:
            exposure_length = float(sys.argv[1])
            gain = float(sys.argv[2])
            num_frames = int(sys.argv[3])
            main_manual(exposure_length, gain, num_frames)
    else:
        main()
