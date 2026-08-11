from picamera2 import Picamera2, Preview
from libcamera import controls
import numpy as np
import time
import os
import subprocess
from datetime import datetime
from tifffile import imwrite
import csv

class CameraLogic:
    # Initialise camera
    def __init__(self, manual=False, config=None, exposure=None):
        try:
            self.picam2 = Picamera2()
        except IndexError as idx_err:
            subprocess.run(["vcgencmd", "get_camera"])
            self.picam2 = Picamera2()

        exposure_microsecs: int
        if exposure is not None:
            exposure_microsecs = int(exposure * 1_000_000)
        else:
            exposure_microsecs = int(500_000) # default to 0.5s

        dimensions = (4056, 3040)
        dimensions_wide = (4608, 2592)

        self.still_config = self.picam2.create_still_configuration(
            main={"size": dimensions},
            raw={"format": "SRGGB12", "size": dimensions},
            sensor={"output_size": dimensions, "bit_depth": 12},
            controls={
                "FrameDurationLimits": (110, 90_000_000),
                "AeEnable": False,
                "AwbEnable": False,
                "ColourGains": (1.0, 1.0),
                #"AfMode": controls.AfModeEnum.Manual,
                "ExposureTime": exposure_microsecs,
                "AnalogueGain": 1.0,
            },
            buffer_count=1,
        )

        self.picam2.configure(self.still_config)
        time.sleep(1)
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
        gain_value = gain  # [1.0, 2.0, 4.0]
        
        changed = False
        if self.still_config["controls"]["ExposureTime"] != exposure_value:
            self.still_config["controls"]["ExposureTime"] = exposure_value
            changed = True

        if self.still_config["controls"]["AnalogueGain"] != gain_value:
            self.still_config["controls"]["AnalogueGain"] = gain_value
            changed = True

        if changed:
            self.picam2.configure(self.still_config)

        time.sleep(0.5)

        print(self.still_config)
        
        capture_dir = f"/home/pi/images/QuadStar/{datetime.now():%Y%m%d_%H%M%S}_e-{exposure_seconds}_g-{gain}_n-{num_exposures}.solve"
        os.makedirs(capture_dir, exist_ok=True)  
       
        
        self.start()

        # Save raw image to file
        for _ in range(num_exposures):
            print(f"taking image, exposure: {exposure_value}") 
            request = self.picam2.capture_request()

            metadata= request.get_metadata()
            print(f"metadata: {metadata}")
            img_filepath = f"{capture_dir}/Ex{metadata['ExposureTime']}_({exposure_seconds}s)_Gain{metadata['AnalogueGain']}_Temp{metadata['SensorTemperature']}_{time.time()}.tiff"
       
            img_array = request.make_array("raw").view(np.uint16)  
            img_array = img_array[:, :-8]

            request.release()

            imwrite(img_filepath, img_array)
            
            median = np.median(img_array)
            with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv", "a") as f:
                writer = csv.writer(f)
                meta_exposure_len = metadata["ExposureTime"] / 1_000_000.0
                writer.writerow([exposure_seconds, median])         

        self.close()
        return capture_dir