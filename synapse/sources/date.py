#!/usr/bin/env python

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
    socket = context.socket(zmq.PUB)
    socket.connect(const.MUX_SINK)
    logging.info(socket)

    while True:
        dt = datetime.now()

        data = np.array([
            dt.weekday(), dt.hour, dt.minute, dt.second,
            ])

        logging.debug((SOURCE, len(data), data))
        msg = pickle.dumps({
            SOURCE: {
                'data': data,
                'sample_rate': fs,
                }
            })
        socket.send_multipart((SOURCE.encode(), msg))

        time.sleep(1./fs)

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    element()

if __name__ == '__main__':
    main()
