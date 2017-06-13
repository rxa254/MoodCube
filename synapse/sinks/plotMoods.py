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
    fig, ax = plt.subplots()
    lines = {}
    im  = plt.imshow(zz, animated=True)
    plt.xticks([])
    plt.yticks([])
    fig.tight_layout()
    packet = recv_data()
    for source, data in next(packet).items():
        #x             = np.arange(len(data))
        z              = data
        #lines[source] = ax.plot(x, data, label=source)
    #ax.legend()
    #ax.autoscale_view(tight=True, scalex=False, scaley=True)
    #ax.set_ylim(-2**16, 2**16)
    #ax.set_ylim(-1, 20)

    #def update(packet):
    #    for source, data in packet.items():
    #        x = np.arange(len(data))
    #        lines[source][0].set_xdata(x)
    #        lines[source][0].set_ydata(data)

    def updatefig(packet):
        for source, data in packet.items():
                z = np.random.randint(low   = 0,
                                      high  = 255,
                                      size  = zz.shape,
                                      dtype = 'uint8')
        im.set_array(z)
    return im,
        
    anim = animation.FuncAnimation(
        fig, updatefig, recv_data,
        interval = 30,
        #blit     = True,
        )
    plt.show()

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    plotJelly()

if __name__ == '__main__':
    main()
