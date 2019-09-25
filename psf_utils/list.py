#!/usr/bin/env python3
# Usage {{{1
"""
List Signals

Usage:
    psf_list [options] [<psf_file>]

Options:
    -l, --long    include signal meta data

<psf_file> need only be given if it differs from the one use previously.
"""

# Imports {{{1
from docopt import docopt
from inform import Error, columns, display, fatal, os_error, warn
from psf_utils import PSF
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

    # List signals {{{2
    try:
        results = PSF(psf_file, sep=':')

        if show_meta:
            nw = uw = kw = 0
            data = []
            for each in results.all_signals():
                if len(each.name) > nw:
                    nw = len(each.name)
                units = results.units_to_unicode(each.units)
                if len(units) > uw:
                    uw = len(units)
                kind = each.type.kind
                kind = kinds.get(kind, kind)
                if len(kind) > kw:
                    kw = len(kind)
                data.append((each.name, units, kind))
            for name, units, kind in data:
                display(f'    {name:<{nw}}  {units:<{uw}}  {kind:<{kw}}')
        else:
            display(columns([s.name for s in results.all_signals()]))
    except Error as e:
        e.terminate()

# get_psf_filename() {{{1
def get_psf_filename(psf_file):
    if not psf_file:
        try:
            with open(saved_psf_file_filename) as f:
                psf_file = f.read().strip()
            display(f'Using {psf_file}:')
        except OSError:
            fatal('missing psf file name.')
    try:
        with open(saved_psf_file_filename, 'w') as f:
            f.write(psf_file)
    except OSError as e:
        warn(os_error(e))
    return psf_file

