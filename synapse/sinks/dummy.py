#!/usr/bin/env python

from __future__ import print_function
import sys
import zmq
import pickle
import signal
import logging

from .. import const

def element():
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.subscribe(u'')

    while True:
        source, msg = socket.recv_multipart()
        data = pickle.loads(msg)
        logging.dummy((source, len(data), data))

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    main()

if __name__ == '__main__':
    main()
