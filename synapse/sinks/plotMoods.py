#!/usr/bin/env python

from __future__ import division
import sys
import zmq
import pickle
import signal
import numpy as np
import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt
from matplotlib import animation
import logging

from .. import const
from .. import opc
from . import proc

sim = 1

def plotJelly(sources, samples=1):
    seconds = int(samples)

    context = zmq.Context()
    socket  = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.setsockopt(zmq.SUBSCRIBE, '')

    process_data = proc.ProcessData(sources, samples)

    def recv_data():
        source, msg = socket.recv_multipart()
        return pickle.loads(msg)

    if sim == True:
        z   = process_data(recv_data())
        fig = plt.figure(30)
        im  = plt.imshow(z, interpolation='spline16')
        plt.xticks([])
        plt.yticks([])
        print('---***---')
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

        jelly = opc.Client(const.OPC_ADDR)

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
