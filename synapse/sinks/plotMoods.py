#!/usr/bin/env python

from __future__ import division
import sys
import zmq
import pickle
import signal
import collections
import numpy as np
import matplotlib
matplotlib.use('qt4agg')  # why we have to use this one?
import matplotlib.pyplot as plt
from matplotlib import animation
import logging

from .. import const
from .. import opc


numStrips        = 8
numLEDperStrip   = 64  # no. of LEDs per strip
numLEDs = numStrips * numLEDperStrip
sim = False


class DataBuffer(object):
    def __init__(self, seconds):
        self.seconds = seconds
        self.collected = collections.OrderedDict()

    def append(self, packet):
        for source, data in packet.iteritems():
            sample_rate = data['sample_rate']

            desired_samples = self.seconds * sample_rate

            # check sample rate corresponds to an integer number of
            # samples for the desired number of seconds
            assert (desired_samples % 1) == 0

            if source not in self.collected:
                self.collected[source] = collections.deque(maxlen=desired_samples)

            self.collected[source].append(data['data'])

    def get(self):
        output = []
        for source, queue in self.collected.iteritems():
            output.append(np.concatenate(queue))
        return np.concatenate(output)


def process_data(db, packet):
    z = packet['audio_blrms']
    zz = np.zeros((numLEDs, 3))
    for i,a in enumerate(list(z)):
        si = i*64
        bit = bin(int(a) | 2**24)[3:]
        CBIT = 8
        c = tuple([int(bit[i*CBIT:(i*CBIT)+CBIT], 2) for i in range(3)])
        for j in (0, 1, 2):
            zz[si:si+64, j] = np.ones(64) * c[j]
            # zz[si:si+64, j] = c[j]
    return zz

    # # for source, data in packet.iteritems():
    # #     logging.info((source, data))
    # db.append(packet)
    # zz = db.get()

    # return zz


def plotJelly(seconds=1):
    seconds = int(seconds)

    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.setsockopt(zmq.SUBSCRIBE, '')

    db = DataBuffer(seconds)

    def recv_data():
        source, msg = socket.recv_multipart()
        return pickle.loads(msg)

    if sim == True:
        z = process_data(recv_data())
        fig = plt.figure(30)
        im  = plt.imshow(z, interpolation='spline16')
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()

        def updatefig(packet):
            z = process_data(db, packet)
            im.set_array(z)

        anim = animation.FuncAnimation(
            fig, process_data, recv_data,
            interval = 100,
            blit     = False,
            )
        plt.show()

    else:

        jelly = opc.Client('localhost:7890')

        while True:
            packet = recv_data()
            z = process_data(db, packet)
            logging.info(len(z))
            # if z:
            #     jelly.put_pixels(z)

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    plotJelly()

if __name__ == '__main__':
    main()
