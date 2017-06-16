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

sim = False

def plotJelly():    
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.setsockopt(zmq.SUBSCRIBE, '')

    def recv_data():
        source, msg = socket.recv_multipart()
        dd          = pickle.loads(msg)
        yield dd

    numStrips        = 8
    numLEDperStrip   = 64  # no. of LEDs per strip
    numLEDs = numStrips * numLEDperStrip
    jelly = opc.Client('localhost:7890')

    black = [ (0,0,0) ] * numLEDs
    white = [ (255,255,255) ] * numLEDs

    # this is the dimensions of the jellyfish
    # 8 tentacles, 64 LEDs / tentacle, 3 colors/LED
    zz = np.random.randint(low   = 0,
                          high  = 255,
                          size  = (numStrips, numLEDperStrip, 3),
                          dtype = 'uint8')

    if sim == True:
        fig = plt.figure(30)
        im  = plt.imshow(zz, interpolation='spline16')
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()
    else:
        jelly.pu_pixels(zz)
        
    packet = recv_data()
    for source, data in next(packet).items():
        #x             = np.arange(len(data))
        z              = data


    def updatefig(packet):
        for source, data in packet.items():
            t = np.arange(len(data))
            z = np.random.randint(low   = 0,
                                  high  = 255,
                                  size  = (8, 64, 3),
                                  dtype = 'uint8')
            N = 8 * 64 * 3
            z = np.abs(data) / 5000
            z = z[0:N].reshape(8,64,3)

            if sim == True:
                im.set_array(z)
            else:
                jelly.pu_pixels(zz)
            #print str(np.random.randint(5))

    if sim == True:
        anim = animation.FuncAnimation(
            fig, updatefig, recv_data,
            interval = 100,
            blit     = False,
            )
        plt.show()

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    plotJelly()

if __name__ == '__main__':
    main()
