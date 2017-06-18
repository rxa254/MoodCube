#!/usr/bin/env python

import sys
import time
import signal
import logging
import argparse
import numpy as np
import collections
import multiprocessing

logging.basicConfig()

from . import mux
from . import sources
from .sources import *
from . import sinks
from .sinks import *
from . import barplot

from . import const
from . import opc


def kill_fc(*args):
    jelly = opc.Client(const.OPC_ADDR)
    jelly.put_pixels(np.zeros((512, 3)))
    sys.exit()

# signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGINT, kill_fc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--plot', action='store_true',
                        help="plot data")
    parser.add_argument('-b', '--barplot', action='store_true',
                        help="plot data")
    parser.add_argument('-j', '--jellyfish', action='store_true',
                        help="Sim Jelly LEDs")
    parser.add_argument('-t', '--testdrive', action='store_true',
                        help="test Drive the Jellyfish")
    parser.add_argument('sources', metavar='SOUCE', nargs='+',
                        help="source spec")

    args  = parser.parse_args()

    procs = collections.OrderedDict()

    source_list = []

    logging.info("initializing sources...")
    for source_str in args.sources:
        source_spec = source_str.split(':')
        source      = source_spec[0]
        source_args = source_spec[1:]
        logging.debug((source, source_args))
        source_list.append(source)

        func = eval('sources.{}.element'.format(source))
        proc = multiprocessing.Process(
            name   = source_str,
            target = func,
            args   = source_args
            )
        proc.daemon       = True
        logging.info(proc)
        procs[source_str] = proc

    logging.info("initializing mux...")
    proc = multiprocessing.Process(
        name   = 'mux',
        target = mux.element,
        args   = [source_list],
        )
    proc.daemon  = True
    logging.info(proc)
    procs['mux'] = proc

    if args.plot:
        logging.info("initializing plotter...")
        proc = multiprocessing.Process(
            name   = 'plot',
            target = sinks.plot.plot,
            )
        proc.daemon   = True
        logging.info(proc)
        procs['plot'] = proc

    if args.barplot:
        logging.info("initializing plotter...")
        proc = multiprocessing.Process(
            name   = 'barplot',
            target = sinks.barplot.plot,
            )
        proc.daemon   = True
        logging.info(proc)
        procs['barplot'] = proc

    if args.jellyfish:
        logging.info("initializing the Tentacles...")
        proc = multiprocessing.Process(
            name   = 'jellyfish',
            target = sinks.plotMoods.plotJelly,
            args   = [source_list],
            )
        proc.daemon   = True
        logging.info(proc)
        procs['plotMoods'] = proc

    if args.testdrive:
        logging.info("starting the test drive...")
        proc = multiprocessing.Process(
            name   = 'testdrive',
            target = sinks.testdrive.plotJelly,
            args   = [source_list],
            )
        proc.daemon   = True
        logging.info(proc)
        procs['plotMoods'] = proc

    logging.info("starting processes...")
    for source, proc in procs.items():
        proc.start()
        logging.info(proc)

    try:
        for source, proc in procs.items():
            proc.join()
    except KeyboardInterrupt:
        raise SystemExit()


if __name__ == '__main__':
    main()
