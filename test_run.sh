#!/bin/bash

03s= '/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/QuadStar/20260807_183147_e-0.3_g-1.0_n-5.done'
05s= '/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/QuadStar/20260807_183141_e-0.5_g-1.0_n-5.done'

prog_dir= "/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/"

source /home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/src/platesolving/.venv/bin/activate

python3 /home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/src/platesolving/QuadSolver.py \
    -f '/home/thomas/Documents/Code/QuadStar/NewQuadstar/QuadStar_Auxillary_Computer/Kieran Test Images/QuadStar/20260807_183141_e-0.5_g-1.0_n-5.done' \
    -t '.tiff' \
    -d /home/thomas/Documents/Code/QuadStar/platesolving/ASTAP_DB \
    -e /opt/astap/astap



#