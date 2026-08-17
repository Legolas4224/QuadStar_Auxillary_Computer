## Running/Using
- Designed for use on a Raspberry Pi 5 running Raspberry Pi OS Lite (trixie), although should work on most other Raspberry Pis 
- For quadstar.service to run you must be using at least 1 Raspberry Pi Camera, we are using the HQ version as out camera \#0 and the wide v3 was \#1 
- Currently the install.sh script installs most dependencies but other may be needed. (We should really go through and fix 
this). Have had some issues with python not seeing libcamera.
- Alot of paths in the shell scripts are hardcoded eg '/home/pi/images'.

notes:
    if the picam is not connected when booted it WILL NOT connect until you reboot!

### Using QuadSolver

QuadSolver is a module that :
1. Converts raw image files to FITS format
2. Measures the properties of the stars in the images to determine if it should be rejected or not (based on eccentricity)
3. Performs a star alignment on all images, which makes sure any movement between frames is removed and stacking will work properly
4. Integrates the images, currently using a sigma clipping rejection method.
5. Calculates the RA/DEC coordinates of the zenith from the defined location based on image timestamps 
6. Populates the integrated image's FITS header with RA/DEC, capture time, and image scale to make it easier for plate solving
7. Runs ASTAP to solve the image and find the precise astrometric solution

#### Instructions:
1. Check all of the Global Params at the top of the file, particularly the file paths and file types. The pixel size and focal length are very important too. Okay it's actually all important!
2. If you aren't already in the virtual environment, run ```source .venv/bin/activate```
3. Run ```pip install -r requirements.txt```
4. Run ```python QuadSolver.py```
6. Sit back and relax

##### Testing runs
To test you can run with:
```
python3 src/platesolving/QuadSolver.py \
    -f '/path/to/raw/images' \
    -t '<.tiff or .dng>' \
    -d /path/to/star/database \
    -e /path/to/astap_cli 
```

#### Limitations:
While QuadSolver is perfect, it isn't yet perfect.


