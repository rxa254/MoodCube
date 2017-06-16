#!/usr/bin/env python3

import sys
import zmq
import pickle
import signal
import argparse
import numpy as np

from . import const

def xmux():
    context = zmq.Context()

    socket_pub = context.socket(zmq.SUB)
    socket_pub.bind('tcp://*:{}'.format(const.MUX_SUB_PORT))

    socket_pub = context.socket(zmq.PUB)
    socket_pub.bind('tcp://*:{}'.format(const.MUX_PUB_PORT))

    sockets = []
    for arg in sub_args:
        name, port = arg.split(':')
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://localhost:{}".format(port))
        # socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.subscribe(u'')
        print((name, socket))
        sockets.append((name, socket))

    while True:
        mux = []
        for name, socket in sockets:
            msg = socket.recv()
            data = pickle.loads(msg)

            print((name, data))
            mux.append((name, data))

    msg = pickle.dumps(mux)
    socket_pub.send(msg)

##########

def main():
    sub_args = sys.argv[1:]
    if len(sub_args) == 0:
        sys.exit("no sources specified")

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    xmux(sub_args)

if __name__ == '__main__':
    main()
