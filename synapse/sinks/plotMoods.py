#!/usr/bin/env python

from __future__ import division
import sys
import zmq
import pickle
import signal
import numpy as np
import matplotlib as mpl
mpl.use('qt4agg')
import matplotlib.pyplot as plt
from matplotlib import animation
import logging

from .. import const
from .. import opc
from . import proc

sim = True

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

    if sim:
        print('---***---')
        z0  = process_data(recv_data())
        print z0
        mpl.rcParams['toolbar'] = 'None'
        fig = plt.figure(figsize=(12,1.5))
        z   = 255 * np.random.random((8,64,3))
        for k in range(8):
            z[k,:,:] = z0[(k*64)+np.arange(64),:]
        im  = plt.imshow(z/255, interpolation='nearest')
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout(pad=0, h_pad=0)
        
        def updatefig(z0):
            packet = recv_data()
            z0 = process_data(packet)

            # convert from 512x3 to 8x64x3
            z   = np.zeros((8,64,3))
            for k in range(8):
                z[k,:,:] = z0[(k*64)+np.arange(64),:]  # 8 x 64 x 3

            im.set_array(z/255)
            

        anim = animation.FuncAnimation(
            fig, updatefig,
            interval = 100,
            blit     = False, # seems to crash if True
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
