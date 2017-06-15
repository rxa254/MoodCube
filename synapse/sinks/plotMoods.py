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

def plotJelly():    
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.subscribe(u'')

    def recv_data():
        source, msg = socket.recv_multipart()
        dd          = pickle.loads(msg)
        yield dd

    # this is the dimensions of the jellyfish
    # 8 tentacles, 64 LEDs / tentacle, 3 colors/LED
    zz = np.random.randint(low   = 0,
                          high  = 255,
                          size  = (8, 64, 3),
                          dtype = 'uint8')
    fig = plt.figure(30)
    #lines = {}
    im  = plt.imshow(zz, interpolation='spline16')
    plt.xticks([])
    plt.yticks([])
    fig.tight_layout()
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

            
            im.set_array(z)
            #print str(np.random.randint(5))

        
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
