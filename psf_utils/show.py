# Usage {{{1
"""
Show Signals

Signals may either be waveforms or single points.
Waveforms are plotted and single points are printed.

Usage:
    show-psf [options] <signal>...

Options:
    -c, --refresh-cache           refresh the cache
    -f <path>, --psf-file <path>  PSF file
    -d, --db                      show the magnitude of the signals in dB
    -m, --mag                     show the magnitude of the signals
    -p, --ph                      show the phase of the signals
    -g, --major-grid              show major grid lines
    -G, --minor-grid              show major and minor grid lines
    -s <file>, --svg <file>       produce graph as SVG file rather than display it
    -t <title>, --title <title>   title
    -M, --mark-points             place marker on each point
    -P, --just-points             do not connect points with lines (implies -M)
    -V, --version                 show version number and exit

The PSF file need only be given if it differs from the one used previously.

Reading large ASCII data files is slow, so show-psf reads the PSF file once,
then pickles the data and writes it to disk. On subsequent runs the pickled data
is used if the pickle file is newer that the corresponding PSF file.

A signal may contain glob characters. For examples, R1:* shows all signals that
start with R1:.

If a signal as specified on the command line contains a dash, it is split into
two pieces, each of which are considered signals that are components of a
differential signal. The two are accessed individually and the difference is
shown. So for example, out_p-out_n results in V(out_p, ount_n) being shown.
There may only be one dash in a signal, and signals with dashes must not contain
glob characters.
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
from .psf import PSF, Quantity
from . import __version__, __released__
from docopt import docopt
import fnmatch
from inform import Error, display, done, fatal, full_stop, os_error, plural, warn
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import warnings
import sys

# Globals {{{1
axis_prec = 9  # can request many digits as unneeded digits are not shown
cursor_prec = 3
print_prec = 4
Quantity.set_prefs(
    map_sf = Quantity.map_sf_to_sci_notation,
    minus = Quantity.minus_sign,
    # include small scale factors for noise power results
    output_sf = 'TGMkmunpfazy',
    prec = axis_prec,
)
warnings.filterwarnings('ignore', category=FutureWarning)
saved_psf_file_filename = '.psf_file'
saved_arguments_filename = '.psf_show_args'
operators = '+ - * /'.split()


# Utilities {{{1
# get_argv() {{{3
def get_argv():
    argv = sys.argv[1:]
    if argv:
        # save the command line arguments for next time
        try:
            with open(saved_arguments_filename, 'w') as f:
                args = [a for a in argv if a not in ['-c', '--refresh-cache']]
                f.write('\n'.join(args))
        except OSError as e:
            warn(os_error(e))
    else:
        # command line arguments not give, reuse previous ones
        try:
            with open(saved_arguments_filename) as f:
                argv = f.read().split('\n')
            display('Using command:', ' '.join(argv))
        except OSError:
            done()
    return argv


# get_psf_filename() {{{2
def get_psf_filename(psf_file):
    if not psf_file:
        try:
            with open(saved_psf_file_filename) as f:
                psf_file = f.read().strip()
            display('Using PSF file:', psf_file)
        except OSError:
            fatal('missing PSF file name.')
    try:
        with open(saved_psf_file_filename, 'w') as f:
            f.write(psf_file)
    except OSError as e:
        warn(os_error(e))
    return psf_file


# in_args() {{{2
def expand_args(signals, args, allow_diff=True):
    # special case args that contain -, they are considered differential signals
    # they should not include glob chars (*, ?)
    selected = set(a for a in args if '-' in a) if allow_diff else set()
    for arg in args:
        selected.update(fnmatch.filter(signals, arg))
    return sorted(selected)


# show_signals() {{{1
def show_signals():
    try:
        # process command line {{{2
        cmdline = docopt(
            __doc__,
            argv = get_argv(),
            version = f"{__version__} ({__released__})"
        )
        psf_file = get_psf_filename(cmdline['--psf-file'])
        args = cmdline['<signal>']
        title = cmdline['--title']
        svg_file = cmdline['--svg']
        dB = cmdline['--db']
        mag = cmdline['--mag']
        phase = cmdline['--ph']
        use_cache = not cmdline['--refresh-cache']
        linestyle = '' if cmdline['--just-points'] else '-'
        marker = '.' if cmdline['--mark-points'] or cmdline['--just-points'] else ''

        # Open PSF file {{{2
        psf = PSF(psf_file, sep=':', use_cache=use_cache)
        sweep = psf.get_sweep()
        to_show = expand_args(psf.signals.keys(), args)

        # Print scalars {{{2
        if not sweep:
            with Quantity.prefs(map_sf=Quantity.map_sf_to_greek, prec=print_prec):
                to_print = []
                width = 0
                for arg in to_show:
                    pair = arg.split('-')
                    if len(pair) == 2:
                        psig = psf.get_signal(pair[0])
                        nsig = psf.get_signal(pair[1])
                        if psig.units != nsig.units:
                            warn(
                                f'incompatible units ({psig.units} != {nsig.units}',
                                culprit=arg
                            )
                        units = psig.units
                        access = psig.access
                        y_data = Quantity(
                            psig.ordinate - nsig.ordinate,
                            psf.units_to_unicode(units)
                        )
                        if access:
                            name = f'{access}({psig.name},{nsig.name})'
                        else:
                            name = f'({psig.name} − {nsig.name})'
                    else:
                        sig = psf.get_signal(arg)
                        access = sig.access
                        name = f'{access}({sig.name})' if access else sig.name
                        y_data = sig.ordinate
                        if hasattr(y_data, 'units'):
                            y_data.units = psf.units_to_unicode(y_data.units)
                    to_print.append((name, y_data))
                    width = max(width, len(name))
                for name, y_data in to_print:
                    display(f'{name:>{width+4}} = {y_data}')
                return

        # Process arguments for graphs {{{2
        waves = []
        y_units = set()
        for arg in to_show:
            use_log_scale = psf.log_y(sweep)
            pair = arg.split('-')
            if len(pair) == 2:
                psig = psf.get_signal(pair[0])
                nsig = psf.get_signal(pair[1])
                name = arg
                if psig.units != nsig.units:
                    warn(
                        f'incompatible units ({psig.units} != {nsig.units}',
                        culprit=arg
                    )
                units = psig.units
                y_data = psig.ordinate - nsig.ordinate
            else:
                sig = psf.get_signal(arg)
                name = arg
                units = sig.units
                y_data = sig.ordinate
            if units == 'Unitless':
                units = ''
            if dB:
                y_data = 20*np.log10(np.absolute(y_data))
                units = 'dB' + (units or '')
                use_log_scale = False
            elif mag:
                y_data = np.absolute(y_data)
            elif phase:
                y_data = np.angle(y_data, deg=True)
                units = '°'
                use_log_scale = False
            elif np.iscomplexobj(y_data):
                y_data = np.absolute(y_data)
            waves.append((name, y_data, units, use_log_scale))
            y_units.add(units)
        if not y_units:
            raise Error(f'{plural(args):no match/es}.', culprit=args)

        # Formatters {{{2
        # create formatter for x-axis values {{{3
        x_units = sweep.units
        x_data = sweep.abscissa
        x_formatter = FuncFormatter(
            lambda v, p: Quantity(v, x_units).render()
        )

        # create formatter for y-axis values {{{3
        y_formatters = {
            u: FuncFormatter(
                lambda v, p, u=u: str(Quantity(v, psf.units_to_unicode(u)))
            )
            for u in y_units
        }

        # create formatter for cursor readout values {{{3
        xy_formatters = {}
        for u in y_units:
            xy_label = "{x},  {y}"
            units = psf.units_to_unicode(u)
            xy_formatters[u] = lambda x, y: xy_label.format(
                x = Quantity(x, x_units).render(prec=cursor_prec),
                y = Quantity(y, units).render(prec=cursor_prec)
            )

        # Generate the graph {{{2
        if svg_file:
            matplotlib.use('SVG')
        figure, axes = plt.subplots(len(y_units), 1, sharex=True, squeeze=False)
        for i, units in enumerate(y_units):
            for sig_name, y_data, sig_units, use_log_scale in waves:
                if sig_units == units:
                    axes[i, 0].plot(
                        x_data, y_data,
                        label = sig_name,
                        marker = marker,
                        linestyle = linestyle,
                        linewidth = 2,
                    )
            axes[i, 0].legend(frameon=False, loc='best')
            axes[i, 0].set_xscale('log' if psf.log_x(sweep) else 'linear')
            axes[i, 0].set_yscale('log' if use_log_scale else 'linear')
            axes[i, 0].xaxis.set_major_formatter(x_formatter)
            axes[i, 0].yaxis.set_major_formatter(y_formatters[units])
            axes[i, 0].format_coord = xy_formatters[units]
            if cmdline['--minor-grid']:
                axes[i, 0].grid(which="both")
            elif cmdline['--major-grid']:
                axes[i, 0].grid(which="major")
            else:
                axes[i, 0].grid(visible=False)
        if title:
            plt.suptitle(title)
        if svg_file:
            plt.savefig(svg_file)
        else:
            plt.show()
    except ValueError as e:
        fatal(full_stop(e))
    except Error as e:
        e.terminate()
    except OSError as e:
        fatal(os_error(e))
    except KeyboardInterrupt:
        done()
