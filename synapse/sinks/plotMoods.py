#!/usr/bin/env python

from __future__ import division
import sys
import zmq
import pickle
import signal
import numpy as np
import matplotlib
matplotlib.use('qt4agg')  # why we have to use this one?
import matplotlib.pyplot as plt
from matplotlib import animation

from .. import const
from .. import opc


numStrips        = 8
numLEDperStrip   = 64  # no. of LEDs per strip
numLEDs = numStrips * numLEDperStrip
sim = False


def process_data(packet):
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


def plotJelly():    
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.setsockopt(zmq.SUBSCRIBE, '')

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
            z = process_data(packet)
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
            z = process_data(packet)
            jelly.put_pixels(z)

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    plotJelly()

if __name__ == '__main__':
    main()
