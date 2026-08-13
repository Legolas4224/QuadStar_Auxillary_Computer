from picamera2 import Picamera2, Preview
from libcamera import controls
import numpy as np
import time
import os
import subprocess
from datetime import datetime
from tifffile import imwrite
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import csv


class CameraLogic:
    # Initialise camera

    def __init__(
        self, manual=False, config=None, exposure=None, wide_cam: bool = False
    ):
        self.wide_cam = wide_cam
        if wide_cam == True :
            print("WARNING: CAMERA SET TO WIDECAM")

        try:
            self.picam2 = Picamera2()
        except IndexError as idx_err:
            subprocess.run(["vcgencmd", "get_camera"])
            self.picam2 = Picamera2()

        assert exposure is not None, "Must give a valid exposure length"
        exposure_microsecs: int = int(exposure * 1_000_000)

        dimensions_normal = (4056, 3040)
        dimensions_wide = (4608, 2592)
        bit_depth = 12

        if wide_cam:
            dimensions = dimensions_wide
            bit_depth = 10
        else:
            dimensions = dimensions_normal

        cam_controls: dict = {
            "FrameDurationLimits": (110, 100_000_000),
            "AeEnable": False,
            "AwbEnable": False,
            "ColourGains": (1.0, 1.0),
            "ExposureTime": exposure_microsecs,
            "AnalogueGain": 1.0,
        }

        self.still_config = self.picam2.create_still_configuration(
            main={"size": dimensions},
            raw={"format": f"SRGGB{bit_depth}", "size": dimensions},
            sensor={"output_size": dimensions, "bit_depth": bit_depth},
            controls=cam_controls,
            buffer_count=1,
        )

        self.picam2.configure(self.still_config)
        self.picam2.start()

        # only for wide camera vv
        if wide_cam:
            self.picam2.set_controls(
                {"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0}
            )
        # time.sleep(1)
        self.preview_started = False

    # Start camera
    def start(self):
        self.picam2.start()

    # Stop and close camera
    def close(self):
        self.picam2.stop()
        self.picam2.close()

    # Display camera view
    def start_preview(self, preview_type=Preview.DRM):
        self.picam2.start_preview(preview_type)
        self.preview_started = True
        self.picam2.start()

    # Stop camera preview
    def stop_preview(self):
        if self.preview_started:
            self.picam2.stop_preview()

    # Return the camera parameters for calibrating
    def supported_controls(self):
        print(self.picam2.camera_controls)

    def run_exposures(self, exposure_seconds, gain, num_exposures):

        exposure_value = int(exposure_seconds * 10**6)
        gain_value = gain  
        
        changed = False
        if self.still_config["controls"]["ExposureTime"] != exposure_value:
            self.still_config["controls"]["ExposureTime"] = exposure_value
            changed = True

        if self.still_config["controls"]["AnalogueGain"] != gain_value:
            self.still_config["controls"]["AnalogueGain"] = gain_value
            changed = True

        print(self.still_config)

        if changed:
            self.picam2.configure(self.still_config)

        time.sleep(0.5)

        print(self.still_config)

        prefix: str = ""
        if self.wide_cam:
            prefix = "wide_"

        capture_dir = f"/home/pi/images/QuadStar/{datetime.now():%Y%m%d_%H%M%S}_{prefix}e-{exposure_seconds}_g-{gain}_n-{num_exposures}.taking"
        os.makedirs(capture_dir, exist_ok=True)

        # Save raw image to file
        for _ in range(num_exposures):
            print(f"taking image, exposure: {exposure_value / 1_000_000}s")
            request = self.picam2.capture_request()

            metadata = request.get_metadata()
            print(f"metadata: {metadata}")
            img_filepath = f"{capture_dir}/{prefix}Ex{metadata['ExposureTime']}_({exposure_seconds}s)_Gain{metadata['AnalogueGain']}_Temp{metadata['SensorTemperature']}_{time.time()}.tiff"

            img_array = request.make_array("raw").view(np.uint16)
            img_array = img_array[:, :-8]

            request.release()

            imwrite(img_filepath, img_array)
 
            meta_exposure_len = metadata["ExposureTime"]
            tolerance = exposure_value / 100
            if not np.abs(meta_exposure_len - exposure_value) <= tolerance:
                print(f"-- Warning: Actual and expected exposures not matched! --\n -> Actual Exposure: {meta_exposure_len}us\n -> Expected Exposure: {exposure_value}us")

            median = np.median(img_array)
            max_pixel_value = 65520.0
            max_value = np.max(img_array)
            count = np.sum(img_array == max_pixel_value)
            with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([exposure_seconds, median, max_value, count])

        capture_dir_renamed = capture_dir.removesuffix(".taking") + ".solve"
        os.rename(capture_dir, capture_dir_renamed)
        self.close()
        return capture_dir_renamed
