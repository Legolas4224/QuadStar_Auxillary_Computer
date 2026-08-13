import numpy as np
import histogram as hist
import radiometric_calibration as RC
import sys
from datetime import datetime, timezone

exp = float(sys.argv[1])
capture_name = sys.argv[2]
print(f"Capturing {exp}s Image...\n")
stats_dict = capture_to_histo(exp, capture_name)
print("Capture Complete\n==============")
print(f"Median: {stats_dict['Median']}\nMean: {stats_dict['Mean']}")

def main(exposure_time, test_name=f"{exposure_time}+{datetime.now()}", send_to_me=True, make_histo=True, ) :
    print("Running image sensor calibration")
    