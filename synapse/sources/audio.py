#!/usr/bin/env python

import sys
import zmq
import json
import pickle
import signal
import pyaudio
import logging
import numpy as np

from .. import const

CHANNELS = 1
RATE = 44100
CHUNK = 512

def element():
    context = zmq.Context()

    socket = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    p = pyaudio.PyAudio()

    stream = p.open(
        input=True,
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=CHUNK,
        )

    while True:
        try:
            samples = stream.read(CHUNK)
        except IOError:
            continue
        dt = np.dtype(np.int16)
        data = np.frombuffer(samples, dtype=dt)

        source = 'audio'
        logging.debug((source, len(data), data))
        msg = pickle.dumps({source: data})
        socket.send_multipart((source.encode(), msg))

##########

def main():
    channels = [int(c) for c in sys.argv[1:]]
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    element(channels)

if __name__ == '__main__':
    main()
