#!/usr/bin/env python

from __future__ import division
import time, sys, signal
import argparse

import numpy as np

import DAQCplate as DAQC

parser = argparse.ArgumentParser(description='Acquire Data from Pi Plate')
parser.add_argument('-f','--fsample', dest='sample_frequency',
                    metavar='fs', type=float,
                    default = 1, help='Prox Sensor sample frequency [Hz]')
args = parser.parse_args()

fs = args.sample_frequency
if __debug__:
    print("Sample Frequency is " + str(fs) + " Hz")
if fs < 1e-3:
    parser.error("Error: sample rate must be > 1e-3 Hz")

rangeLimit = 300

# this is the main loop
j = 0
while j < 1000:
    x = DAQC.getRANGE(0, 0, 'c')  # get distance [cm]
    if x < 0.1:
        x = rangeLimit
    if __debug__: print x
    j += 1
    time.sleep(1/fs)

# this is the output when its done running
# should also catch the CTRL-C



