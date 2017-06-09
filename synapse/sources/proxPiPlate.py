#!/usr/bin/env python

from __future__ import division
import time, sys, signal
import argparse

import numpy as np

import DAQCplate as DAQC


rangeLimit = 666.666

# this is the thing that get the data
def element(fs):
    while True:
        x = DAQC.getRANGE(0, 0, 'c')  # get distance [cm]
        if x < 0.1:
            x = rangeLimit
        if __debug__: print x
        
        time.sleep(1/fs)

# this is the output when its done running
# should also catch the CTRL-C

# ===================================================
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = argparse.ArgumentParser(description='get Data from Pi Plate')
    parser.add_argument('-f','--fsample', dest='sample_frequency',
                    metavar='fs', type=float,
                    default = 1, help='Prox Sensor sample freq. [Hz]')
    args = parser.parse_args()

    fs = args.sample_frequency
    if __debug__:
        print("Sample Frequency is " + str(fs) + " Hz")

    if fs < 1e-3:
        parser.error("Error: sample rate must be > 1e-3 Hz")

    element(fs)

if __name__ == '__main__':
    main()
