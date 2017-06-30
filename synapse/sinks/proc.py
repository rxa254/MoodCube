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
fsample = 5
N = int(t_prox_hist * fsample)
Nsensors = 8
prox = np.zeros((N, Nsensors))
decay_rate = 0.001

audio_target = np.array([0, 0, 0, 0, 0, 0, 0, 0])
audio_target = np.array([1, 1.5, 2.3, 2.5, 4.5, 3.7, 4.3, 3.6])
prox_target  = 1 * np.array([1, 1, 1, 1])


class ProcessData(object):
    def __init__(self, sources, samples):
        # input data ring buffer
        self.db = DataBuffer(sources, samples)

        self.inpLayer = None
        self.oneLayer = None
        self.twoLayer = None
        self.threeLayer = None
        self.fourLayer = None

        
    def __call__(self, packet):
        self.db.append(packet)
        data = self.db.get()
        #logging.info(len(data))
        print "audio = " + np.array_str(data[0:8], precision=2)
        print "prox/time " + np.array_str(data[8:], precision=2)

        def gradd(xx):
            dxx = xx * (1/2)*(1 - 4*(xx-1)**2)
            return dxx

        bias = np.random.randn(numLEDs, 3)
        audio_mask = [1, 2, 3, 4, 5]
        l1_error   = 1 * np.sum(data[audio_mask] - audio_target[audio_mask])
        print l1_error
        
        beta = 1
        l1_prox_error = np.amin(np.abs(data[8:12] - prox_target))
        print l1_prox_error
        
        L_data = len(data)
        
        if self.inpLayer is None:
            self.inpLayer = 0.01 * np.random.rand(L_data, L_data)/np.sqrt(L_data)
            self.oneLayer = 1 * np.random.rand(40, L_data)/np.sqrt(40)
            self.twoLayer = 1 * np.random.rand(65, 40)/np.sqrt(65)
            self.threeLayer = 1 * np.random.rand(3*numLEDs, 65)/np.sqrt(3*numLEDs)

        # print((data.shape, self.inpLayer.shape))
        a  = data
        b  = np.dot(self.inpLayer, a)
        print(b)
        b  = np.tanh(b)/2 + 1
        # print((a.shape, self.secLayer.shape))
        l1_delta = 1 * (l1_error + beta * l1_prox_error) * gradd(b)
        self.inpLayer *= (1-decay_rate)
        self.inpLayer += np.outer(l1_delta, a)

        a = b
        b = np.dot(self.oneLayer, a)
        bb = b
        #b = np.tanh(b)/2 + 1
        l1_delta = 1 * (l1_error + beta * l1_prox_error) * gradd(b)
        self.oneLayer *= (1-decay_rate)
        self.oneLayer += np.outer(l1_delta, a)

        a = b
        b = np.dot(self.twoLayer, a)
        b = np.tanh(b)/2 + 1
        l1_delta = 1 * (l1_error + beta * l1_prox_error) * gradd(b)
        self.twoLayer *= (1-decay_rate)
        self.twoLayer += np.outer(l1_delta, a)
        
        a = b
        b = np.dot(self.threeLayer, a)
        #print(np.array_str(b[0:7]))
        b = np.tanh(b)/2 + 1
        l1_delta = 1 * (l1_error + beta * l1_prox_error) * gradd(b)
        self.threeLayer *= (1-decay_rate)
        self.threeLayer += np.outer(l1_delta, a)


        zz = b
        #zz = np.tanh(zz)/2 + 1
        zz = zz*50
        # print((zz.shape))
        
        bias_noise = 5 * np.random.rand(numLEDs, 3)
        bias_noise *= (l1_error + l1_prox_error)

        bias += 15 * l1_prox_error * np.random.randn(numLEDs, 3)
        #bias = np.remainder(bias, 100)
        

        print "Output zz = " + np.array_str(zz[13:19], precision=3)
        #print "bias dither = " + np.array_str(bias[13:19], precision=2)
        out = zz.reshape(numLEDs, 3) + bias

        #out = np.remainder(out, 100)
        out = np.clip(out, 0, 100)
        # return 512 x 3 matrix for LEDs
        return out
