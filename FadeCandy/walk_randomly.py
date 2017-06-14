#!/usr/bin/env python

# Use the FadeCandy drivers to send random numbers into 64 RGB LEDs
from __future__ import division
import numpy as np
import opc, time, sys, signal
import argparse

parser = argparse.ArgumentParser(description='Randomly Walk the LEDs.')
parser.add_argument('refresh_period', metavar='tau', type=float,
                    help='LED Refresh Period [ms]')
parser.add_argument('step_size', metavar='delta', type=float,
                    help='Step Size of the Walkers')
args = parser.parse_args()

tau   = args.refresh_period
delta = args.step_size

numLEDs = 64 * 8
client = opc.Client('localhost:7890')

black = [ (0,0,0) ] * numLEDs
white = [ (255,255,255) ] * numLEDs

# catch the CTRL-C and die gracefully
def sigint_handler(signum, frame):
        print('\n')
        print('CTRL-C Encountered...Shutting down.\n')
        client.put_pixels(black)
        sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# Initialize the LED state
g = np.floor(np.random.rand(numLEDs, 3) * 255)
client.put_pixels(g)

while True:
    g += delta * 255 * np.random.randn(numLEDs, 3)

    # get remainder. Don't want the random walk to go off
    # to infinity, so this divides out by 255 so if it goes
    # too big it just flips back to zero
    g = np.remainder(g, 255) 
    sleepTime = tau
    #+ np.random.random_sample()

    # take floor() before writing to the driver so we don't send floats
    client.put_pixels(np.floor(g))
    time.sleep(sleepTime)

