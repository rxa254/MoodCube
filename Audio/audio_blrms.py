#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Modified   May-2017, Rana X Adhikari
"""
from __future__ import division
import time, sys, signal
import argparse
#import threading
import pyaudio
import numpy as np
from scipy.signal import welch

parser = argparse.ArgumentParser(description='Acquire audio Data from Mic')
parser.add_argument('-f','--fsample', dest='sample_frequency',
                    metavar='fs', type=float,
                    default = 44100, help='sample frequency [Hz]')
parser.add_argument('-d','--duration', dest='duration',
                        type=float,
                        default = 1e6, help='recording duration [s]')
parser.add_argument('-c','--chunk_size', dest='chunk_size',
                        type=float,
                        default = 0.1, help='chunk size [s]')
args = parser.parse_args()

fs         = args.sample_frequency
chunk_size = args.chunk_size
duration   = args.duration

if __debug__:
    print("Sample Frequency is " + str(fs) + " Hz")
if fs < 1e-5:
    parser.error("Error: sample rate must be > 1e-5 Hz")


    
def die_with_grace():
    stream.stop_stream()
    stream.close()
    p.terminate()
    
# catch the CTRL-C
def sigint_handler(signum, frame):
    print('\n')
    print('CTRL-C Encountered...Shutting down.\n')
    die_with_grace()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

    
RATE  = int(fs)
CHUNK = int(np.floor(chunk_size * RATE))

p      = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                input_device_index=0,
              frames_per_buffer = CHUNK)

# define frequency bands for the BLRMS
#f1 = np.array([30, 100, 300, 1000, 3000])
f_min = 1/chunk_size
f_max = RATE/2
f1 = np.logspace(np.log10(f_min), np.log10(f_max), 7)

#go for a few seconds
i = 0
blrms = np.zeros(len(f1)-1)
while i < duration/chunk_size:
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)

    data = data.astype('float_') # needs to be float for welch

    ff, psd  = welch(data, RATE, nperseg = CHUNK, scaling='spectrum')

    
    for j in range(len(f1) - 1):
        inds = (ff > f1[j]) & (ff < f1[j+1])
        blrms[j] = np.sum(psd[inds])
    
    np.set_printoptions(formatter={'float': '{: 3.2f}'.format})
    print(blrms)
    if __debug__:
        peak = np.average(np.abs(data))*2
        bars = "#"*int(50*peak/2**16)
        print("%04d %05d %s"%(i,peak,bars))

    i += 1

die_with_grace()
