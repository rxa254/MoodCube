#!/usr/bin/env python

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

# Jamie Synapse dependencies
import zmq
import json
import pickle
import logging
from .. import const


# how to die gracefully so that no one notices
def die_with_grace():
    stream.stop_stream()
    stream.close()
    p.terminate()
    
# what to do if  CTRL-C
def sigint_handler(signum, frame):
    print('\n')
    print('CTRL-C Encountered...Shutting down.\n')
    die_with_grace()
    sys.exit(0)


# DEFAULT_FS = 22050
DEFAULT_FS = 44100
DEFAULT_CHUNK_SIZE = 0.2
#DEFAULT_DURATION = 1e6

def element(fs=DEFAULT_FS, chunk_size=DEFAULT_CHUNK_SIZE):
    logging.debug("Sample Frequency is " + str(fs) + " Hz")

    if fs < 1e-5:
        parser.error("Error: sample rate must be > 1e-5 Hz")

    RATE  = int(fs)
    CHUNK = int(np.floor(chunk_size * RATE))

    context = zmq.Context()

    socket  = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    p      = pyaudio.PyAudio()
    stream = p.open(
        input=True,
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        frames_per_buffer=CHUNK)

    # define frequency bands for the BLRMS
    #f1 = np.array([30, 100, 300, 1000, 3000])
    f_min = np.amin((1/chunk_size, 30))    # don't go below 30 Hz
    f_max = RATE/2.1        # slightly below Nyquist freq
    f1    = np.logspace(np.log10(f_min), np.log10(f_max), 7)

    # go for it
    #np.set_printoptions(formatter = {'float': '{: 3.2f}'.format})
    blms = np.ones(len(f1) - 1)
    while True:
        try:
            samples = stream.read(CHUNK)
        except IOError:
            logging.debug('IOError')
            continue
        data     = np.frombuffer(samples, dtype=np.int16)
        data = data.astype('float_')
        logging.debug(data)
        
        ff, psd  = welch(data, RATE, nperseg = CHUNK,
                         detrend = 'linear',
                         scaling = 'spectrum',
                         return_onesided=True)

        if np.amax(psd) > 1e9 or np.amin(psd) < -1e9:
            print(" ")
            print("Large PSD Element: " + str(np.amax(psd)))
            print(" ")

        for j in range(len(f1) - 1):
            inds    = (ff > f1[j]) & (ff < f1[j+1])
            blms[j] = np.sum(psd[inds])      # this is really blrms**2, not blrms
    
        #dt     = np.dtype(np.float_)
        #array  = np.frombuffer(np.log10(blms), dtype=dt)
        #blms = np.log10(blms)
        
        source = 'audio_blrms'
        logging.info((source, len(blms), blms))
        msg    = pickle.dumps({source: blms})
        socket.send_multipart((source.encode(), msg))

        #peak = np.average(np.abs(data))*2
        #bars = "#"*int(50*peak/2**16)
        #logging.debug("%04d %05d %s"%(i,peak,bars))

    # die_with_grace()

# ===============================================
def main():
    #signal.signal(signal.SIGINT, signal.SIG_DFL)
    # this thing catches the ctrl-C
    signal.signal(signal.SIGINT, sigint_handler)

#    parser = argparse.ArgumentParser(description='Acquire audio Data from Mic')
#    parser.add_argument('-f','--fsample', dest='sample_frequency',
#                        metavar='fs', type=float,
#                        default = DEFAULT_FS, help='sample frequency [Hz]')
#    parser.add_argument('-d','--duration', dest='duration',
#                        type=float,
#                        default = DEFAULT_DURATION, help='recording duration [s]')
#    parser.add_argument('-c','--chunk_size', dest='chunk_size',
#                        type=float,
#                        default = DEFAULT_CHUNK_SIZE, help='chunk size [s]')
#    parser.add_argument("-v", "--verbose", help="increase output verbosity",
#                        action="store_true")
#    args = parser.parse_args()
#
#    if args.verbose:
#        logging.basicConfig(level=logging.DEBUG)
#
#    fs         = args.sample_frequency
#    chunk_size = args.chunk_size
#    duration   = args.duration

    element(rate, chunk)

if __name__ == '__main__':
    main()
