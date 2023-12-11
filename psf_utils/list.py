#!/usr/bin/env python3
# Usage {{{1
"""
List Signals

Usage:
    list-psf [options] [<signal>...]

Options:
    -c, --refresh-cache           refresh the cache
    -f <path>, --psf-file <path>  the path of the ASCII PSF file
    -l, --long                    include signal meta data
    -V, --version                 show version number and exit

The PSF file need only be given if it differs from the one used previously.

Reading large ASCII data files is slow, so list-psf reads the PSF file once,
then pickles the data and writes it to disk. On subsequent runs the pickled data
is used if the pickle file is newer that the corresponding PSF file.
"""

# License {{{1
# Copyright (C) 2018-2023 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].


# Imports {{{1
from .show import expand_args, get_psf_filename
from .psf import PSF
from . import __version__, __released__
from docopt import docopt
from inform import Error, columns, display, plural, warn
import warnings

# Globals {{{1
warnings.filterwarnings('ignore', category=FutureWarning)
saved_psf_file_filename = '.psf_file'
kinds = {
    'float double': 'real',
    'complex double': 'complex',
    'int byte': 'integer',
    'int long': 'integer',
    'int': 'integer',
    'string *': 'string',
}


# list_signals() {{{1
def list_signals():
    # Read command line {{{2
    cmdline = docopt(__doc__, version=f"{__version__} ({__released__})")
    args = cmdline['<signal>']
    if not args:
        args = ['*']
    psf_file = get_psf_filename(cmdline['--psf-file'])
    show_meta = cmdline['--long']
    use_cache = not cmdline['--refresh-cache']

    # List signals {{{2
    try:
        psf = PSF(psf_file, sep=':', use_cache=use_cache)

        if show_meta:
            nw = uw = kw = 0  # name width, units width, kind width
            data = []
            for name in expand_args(psf.signals.keys(), args, allow_diff=False):
                if name not in psf.signals:
                    warn('not found.', culprit=name)
                signal = psf.get_signal(name)
                if len(signal.name) > nw:
                    nw = len(signal.name)
                units = psf.units_to_unicode(signal.units)
                if len(units) > uw:
                    uw = len(units)
                kind = signal.type.kind
                kind = kinds.get(kind, kind)
                if len(kind) > kw:
                    kw = len(kind)

                points = None
                if kind != 'string':
                    try:
                        points = len(signal.ordinate)
                    except TypeError:
                        pass
                data.append((signal.name, units, kind, points))
            if not data:
                raise Error(f'{plural(args):no match/es}.', culprit=args)
            for name, units, kind, points in data:
                if points is None:
                    display(f'    {name:<{nw}}  {units:<{uw}}  {kind}')
                else:
                    display(f'    {name:<{nw}}  {units:<{uw}}  {kind:<{kw}}  ({points} points)')
        else:
            signals = expand_args(psf.signals.keys(), args, allow_diff=False)
            if not signals:
                raise Error(f'{plural(args):no match/es}.', culprit=args)
            display(columns(signals))
    except Error as e:
        e.terminate()
