#!/usr/bin/env python

# # MoodCube: plot Moods 
# ### take some data and display a 2D Surface plot

# Library Imports and Python parameter settings
from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Update the matplotlib configuration parameters:
plt.rcParams.update({'font.size': 20,
                     'font.family': 'serif',
                     'figure.figsize': (10, 8),
                     'axes.grid': True,
                     'grid.color': '#555555'})


# this is the dimensions of the jellyfish
# 8 tentacles, 64 LEDs / tentacle, 3 colors/LED
zz = np.zeros((8, 64, 3))

if __debug__:
    print zz.shape
    print zz.dtype



fig = plt.figure(figsize=(8,2))
im  = plt.imshow(zz, animated=True)
fig.tight_layout()
def updatefig(*args):
    z = np.random.randint(low   = 0,
                          high  = 255,
                          size  = zz.shape,
                          dtype = 'uint8')
    im.set_array(z)
    return im,

#leg = plt.legend(loc='best', fancybox=True, fontsize=14)
#leg.get_frame().set_alpha(0.5)
#plt.savefig("TRY.pdf", bbox_inches='tight')
ani = animation.FuncAnimation(fig, updatefig,
                                  interval=500, blit=True)
plt.show()

