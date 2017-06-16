#!/usr/bin/env python3

import sys
import zmq
import time
import pickle
import signal
import numpy as np

def xsrc(port):
    context = zmq.Context()

    socket = context.socket(zmq.PUB)
    socket.connect('tcp://localhost:{}'.format(port))
    print(socket)

    i = 0
    while True:
        name = b'foo'
        body = i
        print((name, body))
        socket.send_multipart((name, pickle.dumps(body)))
        i += 1
        time.sleep(1)

##########

def main():
    port = sys.argv[1]
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    xsrc(port)

if __name__ == '__main__':
    main()
