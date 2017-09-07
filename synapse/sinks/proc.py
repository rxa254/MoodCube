#!/usr/bin/env python

import numpy as np
import collections
import logging


numStrips      = 8
numLEDperStrip = 64  # no. of LEDs per strip
numLEDs        = numStrips * numLEDperStrip
#np.random.seed(137)

learning_rate = 1e-8 # add comments here about what are good vals
decay_rate    = 1 - 1e-8


# how much history of prox sensors to hold
t_prox_hist  = 20
fsample      = 1
N            = int(t_prox_hist * fsample)
Naudio       = 8 # number of audio bands
Nprox        = 4 # number of proximity sensors
Ntime        = 4 # day, hour, min, sec
Nsensors     = Naudio + Nprox + Ntime
prox         = np.zeros((N * Nsensors, ))

audio_target = np.array([0, 0, 1, 1.5, 1.5, 1, 1, 0])  # roughly human 

prox_target  = np.array([1, 1, 1, 1])   # 1 meter
time_target  = np.array([0, 0, 0, 0])   # dummy



def act_fun(x):  
    #y = 1/(1 + np.exp(-x))  # sigmoid function
    #y = np.tanh(x)  # tanh function
    
    y = x
    m = np.where(x <= 0)
    lam = 1
    y[m] = (np.exp(x[m]) - 1)
    y *= lam
    return y 

def dact_fun(x): 
    #y = x * (1-x) # derivative of sigmoid
    #y = 1 - (np.tanh(x))**2  # derivative of tanh
    y = np.ones_like(x)
    m = np.where(x <= 0)
    lam = 1
    y[m] = np.exp(x[m])
    y *= lam
    return y

# forward propagate the input data through the matrices and thresholds
def forward_prop(input_data, weights):
    b = input_data
    neuron_inputs  = {}
    neuron_outputs = {}
    for layer_name in sorted(weights.keys()):
        a = np.dot(weights[layer_name].T, b)  # apply the weight matrices 
        b = act_fun(a)                        # nonlinear thresholding
        v = {layer_name: a}
        w = {layer_name: b}
        neuron_inputs.update(v)
        neuron_outputs.update(w)              # store the neuron outputs
    output_layer_outputs = b
    return neuron_inputs, neuron_outputs, output_layer_outputs


def compute_gradient(self, error_signal, input_data):
    """ See here: http://neuralnetworksanddeeplearning.com/chap2.html"""
    # do the gradients for the last layer first
    delta  = error_signal
    layers = sorted(self.weights.keys())
    delta *= dact_fun(self.neuron_outputs[layers[-1]])
    gradients = { layers[-1] :
              np.outer(self.neuron_outputs[layers[-2]], delta)}
        
    for k in range(2, self.num_layers):
        dz    = dact_fun(self.neuron_inputs[layers[-k]])

        delta = np.dot(self.weights[layers[-k+1]], delta) * dz

        if k == (self.num_layers - 1):
            dw = { layers[-k]:
                   np.outer(input_data, delta)}
        else:
            dw = { layers[-k]:
                   np.outer(self.neuron_outputs[layers[-k-1]], delta)}


        gradients.update(dw)

    return gradients
        

# use the computed gradients to update the weights
def update_weights(weights, expectation_g_squared, g_dict,
                       decay_rate, learning_rate):
    epsilon = 1e-5
    
    for layer_name in sorted(weights.keys()):
        g = g_dict[layer_name]

        expectation_g_squared[layer_name] = decay_rate * \
                           expectation_g_squared[layer_name] + \
                           (1 - decay_rate) * g**2
        weights[layer_name] += (learning_rate * g) /  \
          (np.sqrt(expectation_g_squared[layer_name] + epsilon))
        # reset batch gradient buffer
        g_dict[layer_name] = np.zeros_like(weights[layer_name])

    return weights, expectation_g_squared, g_dict


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


class ProcessData(object):
    def __init__(self, sources, samples):
        # input data ring buffer
        self.db = DataBuffer(sources, samples)

        self.weights        = {}
        self.neuron_inputs  = {}
        self.neuron_outputs = {}
        # To be used with rmsprop algorithm
        # (http://sebastianruder.com/optimizing-gradient-descent/index.html#rmsprop)
        self.expectation_g_squared = {}
        self.g_dict = {}
        self.data = np.zeros((N, Nsensors))
            
    def __call__(self, packet):
        self.db.append(packet)
        x = self.db.get()

        # update data matrix with fresh samples
        self.data[1:-1,:] = self.data[0:-2,:]
        self.data[0,:]    = x

        data = self.data.flatten()
        logging.info(data.shape)
        #logging.info(data)


        logging.debug("audio_blrms = " +
                      np.array_str(data[0:8], precision=3))
        logging.debug("proximity   = " +
                      np.array_str(data[8:12], precision=3))
        logging.debug("datetime    = " +
                      np.array_str(data[12:16], precision=3))

        audio_mask = [1, 2, 3, 4, 5, 6]

        audio_err   = 1 * np.sum(data[audio_mask] - audio_target[audio_mask])
        #l1_error      = 0.1 * np.sum(data[0:8]  - audio_target)
        
        p_mask = [0, 2, 3]
        prox_dat = data[8:12]
        prox_err = np.amin(np.abs(prox_dat[p_mask]
                                       - prox_target[p_mask]))
        #l1_prox_error = 0.1 * np.sum(data[8:12] - prox_target)
        error_signal = audio_err + prox_err 
        
        
        nL = len(data)
        numNeurons = [nL, 4*nL, nL, 3*numLEDs]

        self.num_layers = len(numNeurons)
        
        # build the initial weight matrices
        if len(self.weights) == 0:
            for j in range(self.num_layers - 1):
                w = {str(j):np.random.randn(numNeurons[j],
                            numNeurons[j+1])/np.sqrt(numNeurons[j])}
                self.weights.update(w)
            for layer_name in self.weights.keys():
                #print layer_name
                self.expectation_g_squared[layer_name] = \
                  np.zeros_like(self.weights[layer_name])
                self.g_dict[layer_name] = \
                  np.zeros_like(self.weights[layer_name])

        

        # go forward through the network
        self.neuron_inputs, self.neuron_outputs, output = \
          forward_prop(data, self.weights)

        self.g_dict = compute_gradient(self, error_signal, data)


        self.weights, self.expectation_g_squared, self.g_dict = \
                update_weights(self.weights,
                               self.expectation_g_squared,
                               self.g_dict,
                               decay_rate, learning_rate)
        
        bias_noise = np.random.randn(numLEDs * 3)
        # scale to output range of 100 (lowered from 255 for power)
        output  = 100 * (output + 1) / 2
        output += 0*bias_noise
        
        output  = np.round(output)
        output  = np.clip(output, 0, 100)

        try:
            logging.info("out = " + np.array_str(output[7:15],
                                                 precision = 0))
        except:
            logging.info("Weird value in output to LEDs...")
        
        output = output.reshape(numLEDs, 3)


        # increase brightness of jelly dome head to compensate
        # for bright room
        # -- selects the first 8 LEDs in each strip
        j0 = np.array(range(8))
        j  = j0
        for k in np.arange(1,8):
            j = np.concatenate((j, j0 + k*64))

        # scale the brightness of the 'j' LEDs by a factor of 255/100
        output[j] *= 255/100
        # out = bias_noise
        # return 512 x 3 matrix for LEDs
        return output
