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

SOURCE = 'audio_blrms'
DEFAULT_NBANDS = 8
DEFAULT_CHUNK_SIZE = 0.2

def element(chunk_size=DEFAULT_CHUNK_SIZE, nbands=DEFAULT_NBANDS):
    chunk_size = float(chunk_size)
    fs = const.AUDIO_RATE

    logging.debug("Sample Frequency is " + str(fs) + " Hz")

    if fs < 1e-5:
        parser.error("Error: sample rate must be > 1e-5 Hz")

    CHUNK = int(np.floor(chunk_size * fs))

    context = zmq.Context()

    socket  = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    p      = pyaudio.PyAudio()
    stream = p.open(
        input    = True,
        format   = pyaudio.paInt16,
        channels = const.AUDIO_CHANNEL,
        rate=const.AUDIO_RATE,
        frames_per_buffer=CHUNK)

    # define frequency bands for the BLRMS
    #f1 = np.array([30, 100, 300, 1000, 3000])
    f_min = min(1/chunk_size, 30)    # don't go below 30 Hz
    f_max = fs/2.1        # slightly below Nyquist freq
    f1    = np.logspace(np.log10(f_min), np.log10(f_max), nbands+1)

    # go for it
    #np.set_printoptions(formatter = {'float': '{: 3.2f}'.format})
    blms = np.ones(len(f1) - 1)

    k = -1
    whiteFilt = np.zeros(nbands)

    while True:

        try:
            samples = stream.read(CHUNK)
        except IOError:
            logging.warning((SOURCE, e))
            continue
        data = np.frombuffer(samples, dtype = np.int16)
        data = data.astype('float_')
        
        ff, psd  = welch(data, fs, nperseg = CHUNK,
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

        # whiten
        k += 1
        whiteFilt += blms
        whiteFilt  = whiteFilt / (k+1)
        blms       = blms / whiteFilt
        blms       = np.log10(blms)

        logging.debug((SOURCE, len(blms), blms))

        msg = pickle.dumps({
            SOURCE: {
                'data': blms,
                'sample_rate': 1/chunk_size,
                }
            })

        socket.send_multipart((SOURCE.encode(), msg))

# ===============================================
def main():
    signal.signal(signal.SIGINT, sigint_handler)
    element()

if __name__ == '__main__':
    main()
