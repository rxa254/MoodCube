import numpy as np
import collections
import logging


class DataBuffer(object):
    def __init__(self, sources, samples):
        self.sources = sources
        self.samples = samples
        self.collected = collections.OrderedDict().fromkeys(sources, None)
        for s in self.collected:
            self.collected[s] = collections.deque(maxlen=samples)

    def append(self, packet):
        for source in self.sources:
            data = packet[source]['data']
            self.collected[source].append(data)

    def get(self):
        for s,q in self.collected.iteritems():
            if len(q) < self.samples:
                return None
        output = []
        for source, queue in self.collected.iteritems():
            output.append(np.concatenate(queue))
        out = np.concatenate(output)
        return out


numStrips        = 8
numLEDperStrip   = 64  # no. of LEDs per strip
numLEDs = numStrips * numLEDperStrip
#np.random.seed(137)

# how much histry of prox sensors to hold
t_prox_hist = 1
fsample = 4
N = int(t_prox_hist * fsample)
Nsensors = 8
prox = np.zeros((N, Nsensors))

class ProcessData(object):
    def __init__(self, sources, samples):
        # input data ring buffer
        self.db = DataBuffer(sources, samples)

        self.inpLayer = None
        self.secLayer = None

    def __call__(self, packet):
        self.db.append(packet)
        data = self.db.get()
        logging.info(len(data))
        print(data)

        if self.inpLayer is None:
            self.inpLayer = 1 * np.random.randn(numLEDs, len(data))
            self.secLayer = 1 * np.random.randn(3*numLEDs, numLEDs)

        # print((data.shape, self.inpLayer.shape))
        a  = np.dot(data.T, self.inpLayer.T)
        #print(a)
        #a /= np.amax(a)
        a  = np.tanh(a)
        # print(a)
        # print((a.shape, self.secLayer.shape))
        zz = np.dot(a.T, self.secLayer.T)
        #zz = np.tanh(zz)/2 + 1
        # print((zz.shape))
        bias_noise = 55 * np.random.randn(numLEDs, 3)
        zz = (zz - 100)/2

        print(zz)
        out = zz.reshape(3, numLEDs).T + 0*bias_noise
        # return 512 x 3 matrix for LEDs
        return out
