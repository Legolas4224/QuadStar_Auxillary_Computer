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
                "FrameDurationLimits": (110, 7_000_000),
                "AeEnable": False,
                "AwbEnable": False,
                "ColourGains": (1.0, 1.0),
                "AfMode": controls.AfModeEnum.Manual,
                "ExposureTime": exposure_microsecs,
                "AnalogueGain": 1.0,
            },
            buffer_count=1,
        )

        self.picam2.configure(self.still_config)
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

        print(self.still_config)
        
        capture_dir = f"/home/pi/images/QuadStar/{datetime.now():%Y%m%d_%H%M%S}_e-{exposure_seconds}_g-{gain}_n-{num_exposures}.solve"
        os.makedirs(capture_dir, exist_ok=True)  
        
        self.start()

        # Save raw image to file
        for _ in range(num_exposures):
            t0 = time.time()
            print(f"taking image, exposure: {exposure_value}") 
            request = self.picam2.capture_request()

            t1 = time.time()
            metadata= request.get_metadata()
            print(f"metadata: {metadata}")
            img_filepath = f"{capture_dir}/Ex{metadata['ExposureTime']}_({exposure_seconds}s)_Gain{metadata['AnalogueGain']}_Temp{metadata['SensorTemperature']}_{time.time()}.tiff"
       
            t2 = time.time()
            img_array = request.make_array("raw").view(np.uint16)  
            
            t3 = time.time()
            request.release()

            t4 = time.time()
            imwrite(img_filepath, img_array)
            
            t5 = time.time()
            median = np.median(img_array)
            with open("/home/pi/QuadStar_Auxillary_Computer/img_median.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([exposure_seconds, median])

            print(f"req={t1-t0}, meta={t2-t1}, cap={t3-t2}, rel={t4-t3}, write={t5-t4}")
         

        self.close()

    def collect_calibration_data(self):
        self.picam2.configure(self.still_config)
        self.picam2.start()
        self.picam2.set_controls({"AeEnable": False})
        gain_values = [1.0]  # [1.0, 2.0, 4.0]
        exposure_values = [
            250,
            500,
            1000,
        ]  # [0.11, 0.5, 1, 5, 10, 50, 100, 500, 1000]	#ms
        exposure_values = [ex * 10**3 for ex in exposure_values]

        for exposure in exposure_values:
            for gain in gain_values:
                self.picam2.set_controls({"ExposureTime": int(exposure), "AnalogGain":gain})

                # Save raw image to file
                for _ in range(2):
                    request = self.picam2.capture_request()
                    metadata = request.get_metadata()
                    request.save_dng(
                        f"./data/Ex:{metadata['ExposureTime']}_Gain:{metadata['AnalogueGain']}_Temp:{metadata['SensorTemperature']}_{time.time()}.dng"
                    )
                    request.release()
                    print(
                        f"Took picture at: Ex:{metadata['ExposureTime']} Gain:{metadata['AnalogueGain']} Temp:{metadata['SensorTemperature']} {time.time()}"
                    )

    # Simple function to find the exposure time and gain to reach the target brightness
    # Notes: This works but it converges to the target brightness very slowly, especially if it is overexposed.
    # Next steps: - Try a calibration function, sweep through a range of exposure and gain to quickly get the correct setting
    #            - Or find a math function that converges faster
    # 			 - Try a different method of auto exposure
    def auto_exposure(self, current, target, plate_solving):
        min_exposure, max_exposure = 1000, 1000000
        min_gain, max_gain = 1.0, 16.0

        request = self.request_capture()
        frame = None 
        metadata = request.get_metadata()
        exposure, gain = metadata["ExposureTime"], metadata["AnalogueGain"]
        request.release()

        if plate_solving:
            while current != target:
                scale = target / current
                if gain < max_gain:
                    gain *= scale
                elif exposure < max_exposure:
                    exposure *= scale
                gain = max_gain if gain > max_gain else gain
                exposure = max_exposure if exposure > max_exposure else exposure

                self.set_brightness(int(exposure), gain)
                for _ in range(5):
                    self.capture()

                print(f"Exposure: {exposure}, Gain: {gain}, Brightness: {current}")

                frame = self.capture()
                current = np.percentile(frame, 99)

    def ae_plate_solving_mode(self):
        self.picam2.set_controls({"AeEnable": False})

        # This set controls is just for testing the mode
        self.set_brightness(1000, 1.0)
        for _ in range(5):
            self.capture()

        target_brightness = 253

        print(self.get_metadat())

        while True:
            frame = self.capture()
            current_brightness = np.percentile(frame, 99)
            if current_brightness != target_brightness:
                self.auto_exposure(
                    current_brightness, target_brightness, plate_solving=True
                )
