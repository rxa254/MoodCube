import numpy as np
import collections
import logging


class DataBuffer(object):
    def __init__(self, sources, samples):
        self.sources = sources
        self.samples = samples
        self.collected = collections.OrderedDict().fromkeys(sources, None)
        for s in self.collected:
            self.collected[s] = collections.deque(maxlen = samples)

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
        logging.debug(out)
        return out


numStrips      = 8
numLEDperStrip = 64  # no. of LEDs per strip
numLEDs        = numStrips * numLEDperStrip
#np.random.seed(137)

# how much history of prox sensors to hold
t_prox_hist  = 10
fsample      = 1
N            = int(t_prox_hist * fsample)
Nsensors     = 8 + 4 + 4
prox         = np.zeros((N, Nsensors))

audio_target = np.array([0, 1, 2, 2.5, 2.7, 3, 3.1, 0])  # roughly human 
prox_target  = np.array([1, 1, 1, 1])   # 1 meter
time_target  = np.array([0, 0, 0, 0])   # dummy

class ProcessData(object):
    def __init__(self, sources, samples):
        # input data ring buffer
        self.db = DataBuffer(sources, samples)

        self.inpLayer   = None
        self.twoLayer   = None
        self.threeLayer = None
        self.fourLayer  = None
        self.outLayer   = None

    def __call__(self, packet):
        self.db.append(packet)
        data = self.db.get()
        logging.debug(len(data))
        #print(data)

        print("audio_blrms = " + str(data[0:8]))
        print("proximity   = " + str(data[8:12]))
        print("datetime    = " + str(data[12:16]))
        l1_error      = 0.01 * np.sum(data[0:8]  - audio_target)
        l1_prox_error = 0.01 * np.sum(data[8:12] - prox_target)

        nL = len(data)
        
        if self.inpLayer is None:
            self.inpLayer   = 0.1 * np.random.randn(nL, nL)
            self.twoLayer   = 0.1 * np.random.randn(nL, nL)
            self.threeLayer = 0.1 * np.random.randn(nL, Nsensors)
            self.fourLayer  = 0.1 * np.random.randn(numLEDs, Nsensors)
            self.outLayer   = 0.1 * np.random.randn(3*numLEDs, numLEDs)
            

        # print((data.shape, self.inpLayer.shape))
        a  = np.dot(self.inpLayer, data)
        #print(a)
        #a /= np.amax(a)

        # Exponential Linear Units https://arxiv.org/abs/1511.07289
        #alpha = 1
        #a = alpha * (np.exp(a) - 1)
        a  = np.tanh(a)/2 + 1          # goes from 0->1 as x -> minux to plus inf
        l1_delta = (l1_error + 1 * l1_prox_error) * a
        self.inpLayer += np.outer(l1_delta, data)
        print "Output of input layer = " + str(a[0:5])
        
        #a  = np.tanh(a)/2 + 1
        #print(a)
        #print((a.shape, self.twoLayer.shape))
        b = np.dot(self.twoLayer, a)
        #a = alpha * (np.exp(a) - 1)
        b  = np.tanh(b)/2 + 1
        l1_delta = (l1_error + 1 * l1_prox_error) * b
        self.twoLayer += np.outer(l1_delta, a)
        print "Output of second layer = " + str(b[0:5])

        a = b
        b = np.dot(self.threeLayer, a)
        b = np.tanh(b)/2 + 1
        l1_delta = (l1_error + 1 * l1_prox_error) * b
        self.threeLayer += np.outer(l1_delta, a)
        #print b
        
        #print a.shape
        a = b
        b = np.dot(self.fourLayer, a)
        b = np.tanh(b)/2 + 1
        l1_delta = (l1_error + 1 * l1_prox_error) * b
        self.fourLayer += np.outer(l1_delta, a)
        #print b
        
        zz = np.dot(self.outLayer, b)
        zz = np.tanh(zz)/2 + 1
        #print zz
        
        
        bias_noise = 55 * np.random.randn(numLEDs, 3)
        zz = 100*zz    # scale to output range of 100 (lowered from 255 for power)

        print zz[7:15]
        out = zz.reshape(numLEDs, 3) + (0.0) * bias_noise
        #out = bias_noise
        # return 512 x 3 matrix for LEDs
        return out
