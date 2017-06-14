#!/usr/bin/env python

import sys
import zmq
import json
import pickle
import signal
import logging
import argparse
import numpy as np

from . import const

def element(sources):
    requested_sources = set(sources)

    context = zmq.Context()

    receiver = context.socket(zmq.SUB)
    receiver.bind(const.MUX_SINK)
    for source in requested_sources:
        receiver.subscribe(source)
    logging.info(receiver)

    socket_pub = context.socket(zmq.PUB)
    socket_pub.bind(const.MUX_SOURCE)
    logging.info(socket_pub)

    output    = dict.fromkeys(sources, None)
    collected = set()
    count     = dict.fromkeys(sources, 0)

    while True:
        mux = []

        _, msg = receiver.recv_multipart()
        body   = pickle.loads(msg)

        for source, data in body.items():
            if source in requested_sources:
                # FIXME: how to append data?
                output[source] = data
                logging.debug((source, len(data), data))
                collected.add(source)

                # statistics
                count[source] += 1
                if count[source] > 1:
                    logging.info(count)

        if collected == requested_sources:
            msg = pickle.dumps(output)
            socket_pub.send_multipart((b'MUX', msg))

            output = dict.fromkeys(sources, None)
            collected = set()
            count = dict.fromkeys(sources, 0)

##########

def main():
    sub_args = sys.argv[1:]
    if len(sub_args) == 0:
        sys.exit("no sources specified")

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    element(sub_args)

if __name__ == '__main__':
    main()
