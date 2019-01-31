
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import ndimage

# Update the matplotlib configuration parameters:
plt.rcParams.update({'font.size':      20,
                     'font.family':    'serif',
                     'figure.figsize': (10, 8),
                     'axes.grid':      True,
                     'grid.color':     '#555555'})


# this is the dimensions of the jellyfish
# 8 tentacles, 64 LEDs / tentacle, 3 colors/LED
d = 2**7
Nbits = 24
cmap = 'nipy_spectral'
#cmap = 'inferno'

zz = np.random.randint(low   = 0,
                       high  = 2**Nbits - 1,
                       size  = (d, d),
                       dtype = 'uint')




fig = plt.figure()
im  = plt.imshow(zz, animated = True,
                interpolation = 'hermite',
                         cmap = cmap)
plt.xticks([])
plt.yticks([])
fig.tight_layout()
def updatefig(*args):
    z = np.random.randint(low   = 0,
                          high  = 2**Nbits - 1,
                          size  = zz.shape,
                          dtype = 'uint')
    
    input_ = np.fft.fft2(z)
    result = ndimage.fourier_gaussian(input_, sigma=1)
    z = np.fft.ifft2(result)
    z = np.abs(z)
    
    im.set_array(z)
    
    return im,

#leg = plt.legend(loc='best', fancybox=True, fontsize=14)
#leg.get_frame().set_alpha(0.5)
#plt.savefig("TRY.pdf", bbox_inches='tight')
ani = animation.FuncAnimation(fig, updatefig,
                                  interval = 200,
                                  blit = True)
plt.show()

