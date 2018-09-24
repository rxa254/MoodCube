# Library Imports and Python parameter settings


import numpy as np
import matplotlib.pyplot as plt



# Update the matplotlib configuration parameters:
#plt.rcParams.update({'font.size': 20,
#                     'font.family': 'serif',
#                     'figure.figsize': (10, 8),
#                     'axes.grid': True,
#                     'grid.color': '#555555'})


# this is the dimensions of display grid
d = 2**8
zz = np.random.randint(low   = 0,
                          high  = 2**24,
                          size  = (d, d),
                          dtype = 'uint')


fig = plt.figure(figsize=(8,8))
im  = plt.imshow(zz, cmap='gist_rainbow',
                     interpolation='hermite')
plt.xticks([])
plt.yticks([])
fig.tight_layout()


plt.savefig('gravatar.png', bbox_inches='tight')

