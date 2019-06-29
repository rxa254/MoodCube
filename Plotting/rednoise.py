# this makes a running surf noise plot

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import ndimage
import signal
import sys
def signal_handler(sig, frame):
        print('User Interrupt detected.')
        sys.exit(0)

# Update the matplotlib configuration parameters:
plt.rcParams.update({'font.size':      20,
                     'font.family':    'serif',
                     'figure.figsize': (10, 8),
                     'axes.grid':      True,
                     'grid.color':     '#555555'})

signal.signal(signal.SIGINT, signal_handler)
# this is the dimensions of the jellyfish
# 8 tentacles, 64 LEDs / tentacle, 3 colors/LED
d     = 2**8
Nbits = 0
cmap  = 'nipy_spectral'
#cmap='gnuplot'
#cmap = 'copper'
#cmap = 'inferno'


mu    = 0.0
sigma = 0.01
zz    = np.random.randn(d, d)
zz    = sigma*zz + mu
#zz = zz.astype(int)

fig   = plt.figure()
im    = plt.imshow(zz * 2**Nbits, animated = True,
                   interpolation = 'gaussian', aspect='equal',
                   cmap=cmap, vmin=0, vmax=1)

plt.xticks([])
plt.yticks([])
fig.tight_layout()
def updatefig(*args):

        global zz
        mu    = 0.0
        sigma = 1.5

        # random dist w/ offset of mu
        dz = sigma * np.random.randn(d, d) + mu
        #dz2 = sigma * np.random.randn(d, d) + mu
        #dz = np.random.lognormal(mean=mu, sigma=sigma, size = (d,d))

        # add some outliers to make it non-Gaussian

        z = 0.95*zz + 0.05*dz#combination of past and present
        zz = z # update the memory holder

        # make sure it fits in the range
        z = np.clip(z, 0, 1)
        im.set_array(z * 2**Nbits)
    
        return im,

ani = animation.FuncAnimation(fig, updatefig,
                                  interval = 420,
                                  blit = True)
plt.show()

