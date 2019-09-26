#!/usr/bin/env python3
# Usage {{{1
"""
List Signals

Usage:
    list_psf [options] [<psf_file>]

Options:
    -l, --long       include signal meta data
    -c, --no-cache   ignore, then regenerate, the cache

<psf_file> need only be given if it differs from the one use previously.
"""

# Imports {{{1
from .plot import get_psf_filename
from .psf import PSF
from docopt import docopt
from inform import Error, columns, display, fatal, os_error, warn
import warnings

# Globals {{{1
warnings.filterwarnings('ignore', category=FutureWarning)
saved_psf_file_filename = '.psf_file'
kinds = {
    'float double': 'real',
    'float complex': 'complex',
}

# list_signals() {{{1
def list_signals():
    # Read command line {{{2
    cmdline = docopt(__doc__)
    psf_file = get_psf_filename(cmdline['<psf_file>'])
    show_meta = cmdline['--long']
    use_cache = not cmdline['--no-cache']

    # List signals {{{2
    try:
        psf = PSF(psf_file, sep=':', use_cache=use_cache)

        if show_meta:
            nw = uw = kw = 0
            data = []
            for signal in psf.all_signals():
                if len(signal.name) > nw:
                    nw = len(signal.name)
                units = psf.units_to_unicode(signal.units)
                if len(units) > uw:
                    uw = len(units)
                kind = signal.type.kind
                kind = kinds.get(kind, kind)
                if len(kind) > kw:
                    kw = len(kind)
                points = len(signal.ordinate)
                data.append((signal.name, units, kind, points))
            for name, units, kind, points in data:
                display(f'    {name:<{nw}}  {units:<{uw}}  {kind:<{kw}}  ({points} points)')
        else:
            display(columns([s.name for s in psf.all_signals()]))
    except Error as e:
        e.terminate()
