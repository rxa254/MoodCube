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

from .. import const

def plot():    
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.setsockopt(zmq.SUBSCRIBE, '')

    def recv_data():
        source, msg = socket.recv_multipart()
        dd          = pickle.loads(msg)
        yield dd

    fig, ax = plt.subplots()
    lines = {}
    packet = recv_data()
    for source, data in next(packet).items():
        x             = np.arange(len(data))
        lines[source] = ax.plot(x, data, label=source, marker='.')
    #ax.legend()
    ax.autoscale_view(tight=True, scalex=False, scaley=True)
    #ax.set_ylim(-2**16, 2**16)
    #ax.set_ylim(-1, 20)

    def update(packet):
        for source, data in packet.items():
            x = np.arange(len(data))
            lines[source][0].set_xdata(x)
            lines[source][0].set_ydata(data)
        
    anim = animation.FuncAnimation(
        fig, update, recv_data,
        interval=3,
        # blit=False,
        # repeat=False,
        )
    plt.show()

##########

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    plot()

if __name__ == '__main__':
    main()
