import numpy as np
import collections
import logging

def act_fun(x):  
    #y = 1/(1 + np.exp(-x))  # sigmoid function
    y = np.tanh(x)  # tanh function
    #y = x
    #m = np.any([x <= 0])
    #alpha = 1
    #y[m] = alpha * (np.exp(x) - 1)
    return y 

def dact_fund(x): 
    #y = x * (1-x) # derivative of sigmoid
    y = 1 - x**2  # derivative of tanh
    #y = 1
    #m = np.any([x <= 0])
    #alpha = 1
    #y[m] = x + alpha
    return y

# forward propagate the input data through the matrices and thresholds
def forward_prop(input_data, weights):
    b = input_data
    for layer_name in sorted(weights.keys()):
        b = np.dot(weights[layer_name].T, b)
        b = act_fun(b)
    return b

def compute_gradient(gradient_log_p, hidden_layer_values,
                         input_data, weights):
    """ See here: http://neuralnetworksanddeeplearning.com/chap2.html"""
    delta_L = gradient_log_p
    dC_dw2 = np.dot(hidden_layer_values.T, delta_L).ravel()
    delta_l2 = np.outer(delta_L, weights['2'])
    delta_l2 = relu(delta_l2)
    dC_dw1 = np.dot(delta_l2.T, observation_values)
    return {
        '1': dC_dw1,
        '2': dC_dw2
    }

# use the computed gradients to update the weights
def update_weights(weights, expectation_g_squared, g_dict,
                       decay_rate, learning_rate):
    epsilon = 1e-5
    for layer_name in sorted(weights.keys()):
        g = g_dict[layer_name]
        expectation_g_squared[layer_name] = decay_rate * \
          expectation_g_squared[layer_name] + (1 - decay_rate) * g**2
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

        self.weights = {}

            
    def __call__(self, packet):
        self.db.append(packet)
        data = self.db.get()
        logging.debug(len(data))
        #print(data)


        print("audio_blrms = " + np.array_str(data[0:8], precision=3))
        print("proximity   = " + np.array_str(data[8:12], precision=3))
        print("datetime    = " + np.array_str(data[12:16], precision=3))
        l1_error      = 0.1 * np.sum(data[0:8]  - audio_target)
        l1_prox_error = 0.1 * np.sum(data[8:12] - prox_target)

        nL = len(data)

        numNeurons = [nL, nL, 3*numLEDs]

        # build the initial weight matrices
        if len(self.weights) == 0:
            for j in range(len(numNeurons)-1):
                w = {str(j):np.random.randn(numNeurons[j], numNeurons[j+1])}
                self.weights.update(w)
        
        # To be used with rmsprop algorithm
        # (http://sebastianruder.com/optimizing-gradient-descent/index.html#rmsprop)
        expectation_g_squared = {}
        g_dict = {}
        for layer_name in self.weights.keys():
            expectation_g_squared[layer_name] = np.zeros_like(self.weights[layer_name])
            g_dict[layer_name] = np.zeros_like(self.weights[layer_name])

        # go forward through the network
        output = forward_prop(data, self.weights)
        
        bias_noise = np.random.randn(numLEDs, 3)
        # scale to output range of 100 (lowered from 255 for power)
        output = 100 * (output + 1) / 2

        print("out = " + np.array_str(output[7:15], precision=2))
        output = output.reshape(numLEDs, 3) + (0) * bias_noise
        #out = bias_noise
        # return 512 x 3 matrix for LEDs
        return output
