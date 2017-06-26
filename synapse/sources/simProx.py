#!/usr/bin/env python
# coding: utf-8

# # make some fake Data
# ## this generates some simulated data for use with the MoodCube Synapse
# ### data is packaged to be used for reinforcement learning in the JellyFish
#
# data is broadcast on Zero MQ for ingestion by Neural Network ?

from __future__ import division
from scipy.stats import rayleigh
from timeit import default_timer as timer

import time, sys, signal
import argparse
#import threading
#import pyaudio
import numpy as np

# Jamie Synapse dependencies
import zmq
import json
import pickle
import logging
from .. import const


# ### Functions to make simulated Raspberry Pi data

# temeprature sensorss
def TemperatureData(t, T_0, dT):
    T = T_0 * np.ones_like(t)   # average temperature is T_0 [deg C]
    for ii in range(len(T)):
        deltaT = np.random.normal(0, dT/100)
        T[ii] = T[ii-1] + deltaT

    return T

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

# simulate the spectral BL-MS output of a microphone
def AudioSpectrumData(t, Nbands):
    # Nbands = # of frequency bands
    npts = len(t)
    blms = np.zeros((npts, Nbands))
    for jj in range(Nbands):
        blms[:,jj] = rayleigh.rvs(size = npts)

    return blms

DEFAULT_FS = 1
DEFAULT_CHUNK_SIZE = 1
SOURCE = 'proximity'

def element(fs = DEFAULT_FS, chunk_size = DEFAULT_CHUNK_SIZE):


    # mke some data
    fsample = fs     # [Hz]
    dur     = chunk_size   # seconds
    tt      = np.arange(start = 0, stop = dur, step = 1/fsample)

    Nprox   = 4
    d_mean  = 50

    context = zmq.Context()
    socket  = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    while True:
        #T    = TemperatureData(tt, 25, 2)            #  deg C
        ds   = ProximityData(tt, d_mean, 5, Nprox)   #  [cm]
        #blms = AudioSpectrumData(tt, Nbands)         # decibels
        array = ds

        logging.debug((SOURCE, len(data), data))
        #msg    = pickle.dumps({source: array})
        msg = pickle.dumps({
            SOURCE: {
                'data'       : data,
                'sample_rate': fs,
                }
            })
        socket.send_multipart((source.encode(), msg))

        time.sleep(1/fs)


# ===============================================
def main():

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # this thing catches the ctrl-C
    #signal.signal(signal.SIGINT, sigint_handler)

    element()

if __name__ == '__main__':
    main()
