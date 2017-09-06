#!/usr/bin/env python

from __future__ import division
import sys
import zmq
import time
import pickle
import signal
import logging
from datetime import datetime
import numpy as np

from .. import const

SOURCE = 'date'

def element(fs=1):
    fs = float(fs)

    context = zmq.Context()
    socket  = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    while True:
        dt = datetime.now()

        # normalize to have zero mean
        # and go +/- 0.5
        data = np.array([
            dt.weekday()/6 - 0.5,
            dt.hour/23     - 0.5,
            dt.minute/59   - 0.5,
            dt.second/59   - 0.5,
            ])

        logging.debug((SOURCE, len(data), data))
        msg = pickle.dumps({
            SOURCE: {
                'data': data,
                'sample_rate': fs,
                }
            })
        socket.send_multipart((SOURCE.encode(), msg))

        time.sleep(1/fs)

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    element()

if __name__ == '__main__':
    main()
