#!/usr/bin/env python3

import sys
import zmq
import pickle
import signal
import numpy as np
import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt
from matplotlib import animation

from . import const

def plot():    
    context = zmq.Context()

    socket = context.socket(zmq.SUB)
    socket.connect(const.MUX_SOURCE)
    socket.subscribe(u'')

    def recv_data():
        source, msg = socket.recv_multipart()
        dd = pickle.loads(msg)
        yield dd

    fig, ax = plt.subplots()
    lines = {}
    packet = recv_data()
    for source, data in packet.__next__().items():
        x = np.arange(len(data))
        lines[source] = ax.plot(x, data, label=source)
    ax.legend()
    ax.set_ylim(-2**16, 2**16)

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
