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

audio_target = np.array([0, 1, 2, 2.5, 2.7, 3, 3.1, 0]) 
prox_target = np.array([1, 1, 1, 1])

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
        
        l1_error = np.sum(data[0:8] - audio_target)

        l1_prox_error = np.sum(data[8:12] - prox_target)
        
        if self.inpLayer is None:
            self.inpLayer = 1 * np.random.randn(numLEDs, len(data))
            self.secLayer = 1 * np.random.rand(3*numLEDs, numLEDs)

        # print((data.shape, self.inpLayer.shape))
        a  = np.dot(data.T, self.inpLayer.T)
        #print(a)
        #a /= np.amax(a)

        # Exponential Linear Units https://arxiv.org/abs/1511.07289
        #alpha = 1  
        #a = alpha * (np.exp(a) - 1)

        a  = np.tanh(a)/2 + 1
        # print(a)
        # print((a.shape, self.secLayer.shape))
        zz = np.dot(a.T, self.secLayer.T)
        #zz = np.tanh(zz)/2 + 1
        # print((zz.shape))

        l1_delta = (0.3 * l1_error + 1 * l1_prox_error) * a
        self.inpLayer += np.outer(l1_delta, data)

        
        bias_noise = 55 * np.random.randn(numLEDs, 3)
        zz = (zz - 100)/2

        print(zz)
        out = zz.reshape(3, numLEDs).T + 3/l1_error*bias_noise
        # return 512 x 3 matrix for LEDs
        return out
