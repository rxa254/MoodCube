#!/usr/bin/env python

import sys
import time
import logging
import argparse
import importlib
import collections
import multiprocessing

logging.basicConfig()

from . import mux
from . import sources
from . import sinks
from .sources import audio
from .sources import audio_blrms
from .sources import simProx
from .sinks import plotMoods
from . import plot
from . import barplot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--plot', action='store_true',
                        help="plot data")
    parser.add_argument('-b', '--barplot', action='store_true',
                        help="plot data")
    parser.add_argument('-j', '--jellyfish', action='store_true',
                        help="Sim Jelly LEDs")
    parser.add_argument('sources', metavar='SOUCE', nargs='+',
                        help="source spec")

    args  = parser.parse_args()

    procs = collections.OrderedDict()

    logging.info("initializing mux...")
    proc = multiprocessing.Process(
        name   = 'mux',
        target = mux.element,
        args   = [args.sources],
        )
    proc.daemon  = True
    logging.info(proc)
    procs['mux'] = proc

    logging.info("initializing sources...")
    for source_str in args.sources:
        source_spec = source_str.split(':')
        source      = source_spec[0]
        source_args = source_spec[1:]
        logging.debug((source, source_args))

        func = eval('sources.{}.element'.format(source))
        proc = multiprocessing.Process(
            name   = source_str,
            target = func,
            args   = source_args
            )
        proc.daemon       = True
        logging.info(proc)
        procs[source_str] = proc

    if args.plot:
        logging.info("initializing plotter...")
        proc = multiprocessing.Process(
            name   = 'plot',
            target = plot.plot,
            )
        proc.daemon   = True
        logging.info(proc)
        procs['plot'] = proc

    if args.barplot:
        logging.info("initializing plotter...")
        proc = multiprocessing.Process(
            name   = 'barplot',
            target = barplot.plot,
            )
        proc.daemon   = True
        logging.info(proc)
        procs['barplot'] = proc

    if args.jellyfish:
        logging.info("initializing the Tentacles...")
        proc = multiprocessing.Process(
            name   = 'jellyfish',
            target = plotMoods.plotJelly,
            )
        proc.daemon   = True
        logging.info(proc)
        procs['plotJelly'] = proc

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
