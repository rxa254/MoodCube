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


numStrips        = 8
numLEDperStrip   = 64  # no. of LEDs per strip
numLEDs = numStrips * numLEDperStrip
sim = True
#np.random.seed(137)

# how much histry of prox sensors to hold
t_prox_hist = 1
fsample = 4
N = int(t_prox_hist * fsample)
Nsensors = 8
prox = np.zeros((N, Nsensors))

inpLayer = 3 * np.random.rand(numLEDs, N)
secLayer = 1 * np.random.rand(Nsensors, 3)

k = 0
whiteFilt = np.zeros(Nsensors)

def process_data(packet):
    global k, whiteFilt
    z       = packet['audio_blrms']
    fsample = z['sample_rate']
    
    data      = np.asarray(z['data'])
    #data     = data / 0.001   # scale to unity
    logging.debug(k)
    prox[1:] = prox[0:-1]
    prox[0]  = data
    # Exponential Linear Units https://arxiv.org/abs/1511.07289
    #alpha = 1  
    #a = alpha * (np.exp(a) - 1)

    a  = np.dot(prox.T, inpLayer.T)
    a  = np.tanh(a)/2 + 1
    zz = np.dot(a.T, secLayer)
    #zz = np.tanh(zz)/2 + 1
    logging.debug("zz shape = " + str(zz.shape))
    #zz      = np.zeros(numLEDs * 3)
    
    # return 512 x 3 matrix for LEDs
    zz = 25 * zz + 555

    
    k += 1
    zz = np.floor(np.clip(zz, 0, 100))
    return zz


def plotJelly(sources, seconds=1):
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
        # init
        jelly.put_pixels(np.zeros((numLEDs, 3)))
        k = 0
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
