#!/usr/bin/env python

from __future__ import division
import time, sys, signal
import argparse

import numpy as np
from scipy.stats import rayleigh
#import DAQCplate as DAQC

# Jamie Synapse dependencies
import zmq
import pickle
import logging
from .. import const

rangeLimit = 666.666

# simulated data
# random distance data from N UltraSonic proximity sensors
def ProximityData(t, d_0, dx, N):
    # average distance = d_0
    # movement scale is dx
    # number of prox sensors = N
    d = d_0 * np.ones((len(t), N))   # average distance is d_0 [m]
    for ii in range(len(t)):
        for jj in range(N):
            deltaX   = rayleigh.rvs() - 1 
            d[ii,jj] = d[ii-1,jj] + deltaX

    return d

sim = True

SOURCE = 'proximity'
Nprox   = 4
d_mean  = 100   # average distance for sim data
# this is the thing that get the data
def element(fsample):

    fs = int(fsample)

    context = zmq.Context()
    socket  = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)
        
    while True:
        # do SIM if sample frequency negative
        if sim:
            t = [1]
            ds    = ProximityData(t, d_mean, 15, Nprox)   #  [cm]
            data  = np.asarray(ds[0])/100
            #print data
            logging.debug(data)
        else:
            #vv = 39
            x1 = DAQC.getRANGE(0, 0, 'c')  # get distance [cm]
            x2 = DAQC.getRANGE(0, 1, 'c')  # get distance [cm]
            x3 = DAQC.getRANGE(0, 2, 'c')  # get distance [cm]
            x4 = DAQC.getRANGE(0, 3, 'c')  # get distance [cm]
            if x1 < 0.1:
                x1 = rangeLimit
            data = np.asarray([x1, x2, x3, x4]) / 100   # cm to m


        logging.debug((SOURCE, len(data), data))
        msg = pickle.dumps({
            SOURCE: {
                'data'       : data,
                'sample_rate': fs,
                }
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
