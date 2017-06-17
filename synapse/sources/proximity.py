#!/usr/bin/env python

from __future__ import division
import time, sys, signal
import argparse

import numpy as np

import DAQCplate as DAQC

# Jamie Synapse dependencies
import zmq
import pickle
import logging
from .. import const

rangeLimit = 666.666

SOURCE = 'proximity'
# this is the thing that get the data
def element(fs):

    context = zmq.Context()

    socket  = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    while True:
        x1 = DAQC.getRANGE(0, 0, 'c')  # get distance [cm]
        x2 = DAQC.getRANGE(0, 1, 'c')  # get distance [cm]
        x3 = DAQC.getRANGE(0, 2, 'c')  # get distance [cm]
        x4 = DAQC.getRANGE(0, 3, 'c')  # get distance [cm]
        if x1 < 0.1:
            x1 = rangeLimit
        data = [x1, x2, x3, x4]
        if __debug__:
            print(data)

        logging.debug((SOURCE, len(data), data))
        msg = pickle.dumps({
            'source'     : SOURCE,
            'data'       : data,
            'sample_rate': fs,
            })
        socket.send_multipart((SOURCE.encode(), msg))

        time.sleep(1/fs)

# this is the output when its done running
# should also catch the CTRL-C

# ===================================================
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description='get Data from Pi Plate')
    parser.add_argument('-f','--fsample', dest='sample_frequency',
                    metavar='fs', type=float,
                    default = 2, help='Prox Sensor sample freq. [Hz]')
    args = parser.parse_args()

    fs = args.sample_frequency
    if __debug__:
        print("Sample Frequency is " + str(fs) + " Hz")

    if fs < 1e-3:
        parser.error("Error: sample rate must be > 1e-3 Hz")

    element(fs)

if __name__ == '__main__':
    main()
