# Usage {{{1
"""
Plot Signals

Usage:
    plot-psf [options] <signal>...

Options:
    -c, --no-cache                ignore, then regenerate, the cache
    -f <path>, --psf-file <path>  PSF file
    -d, --db                      plot the magnitude of the signals in dB
    -m, --mag                     plot the magnitude of the signals
    -p, --ph                      plot the phase of the signals
    -s <file>, --svg <file>       produce plot as SVG file rather than display it
    -t <title>, --title <title>   title

The PSF file need only be given if it differs from the one used previously.

Reading large ASCII data files is slow, so plot-psf reads the PSF file once,
then pickles the data and writes it to disk. On subsequent runs the pickled data
is used if the pickle file is newer that the corresponding PSF file.

A signal may contain glob characters. For examples, R1:* plots all signals that
start with R1:.

If a signal as specified on the command line contains a dash, it is split into
two pieces, each of which are considered signals that are components of a
differential signal. The two are accessed individually and the difference is
plotted. So for example, out_p-out_n results in V(out_p, ount_n) being plotted.
There may only be one dash in a signal, and signals with dashes must not contain
glob characters.
"""


# Imports {{{1
from .psf import PSF
from docopt import docopt
import fnmatch
from inform import (
    Error, Info, conjoin, display, done, fatal, os_error, plural, render, warn
)
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, EngFormatter
import numpy as np
from quantiphy import Quantity
Quantity.set_prefs(
    map_sf = Quantity.map_sf_to_sci_notation,
    minus = Quantity.minus_sign,
    output_sf = 'TGMkmunpfazy',
        # include small scale factors for noise power results
    prec = 2,
)
from shlib import Run, set_prefs
set_prefs(use_inform=True)
import warnings
import sys

# Globals {{{1
warnings.filterwarnings('ignore', category=FutureWarning)
saved_psf_file_filename = '.psf_file'
saved_arguments_filename = '.psf_plot_args'
operators = '+ - * /'.split()

# plot_signals() {{{1
def plot_signals():
    try:
        # process command line {{{2
        cmdline = docopt(__doc__, argv=get_argv())
        psf_file = get_psf_filename(cmdline['--psf-file'])
        args = cmdline['<signal>']
        title = cmdline['--title']
        svg_file = cmdline['--svg']
        dB = cmdline['--db']
        mag = cmdline['--mag']
        phase = cmdline['--ph']
        use_cache = not cmdline['--no-cache']

        # Open PSF file {{{2
        psf = PSF(psf_file, sep=':', use_cache=use_cache)
        sweep = psf.get_sweep()
        x_name = sweep.name
        x_units = sweep.units
        x_data = sweep.abscissa

        x_formatter = FuncFormatter(
            lambda v, p: Quantity(v, x_units).render()
        )

        # Process arguments {{{2
        to_plot = expand_args(psf.signals.keys(), args)
        waves = []
        y_units = set()
        for arg in to_plot:
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
            if dB:
                y_data = 20*np.log10(np.absolute(y_data))
                units = 'dB' + units
            elif mag:
                y_data = np.absolute(y_data)
            elif phase:
                y_data = np.angle(y_data, deg=True)
                units = '°'
            elif np.iscomplexobj(y_data):
                y_data = np.absolute(y_data)
            waves.append((name, y_data, units))
            y_units.add(units)
        if not y_units:
            raise Error(f'{plural(args):no match/es}.', culprit=args)

        y_formatters = {
            u:FuncFormatter(
                lambda v, p, u=u: str(Quantity(v, psf.units_to_unicode(u)))
            )
            for u in y_units
        }

        # Generate the plot {{{2
        if svg_file:
            matplotlib.use('SVG')
        figure, axes = plt.subplots(len(y_units), 1, sharex=True, squeeze=False)
        for i, units in enumerate(y_units):
            for sig_name, y_data, sig_units in waves:
                if sig_units == units:
                    axes[i,0].plot(
                        x_data, y_data,
                        linewidth=2, label=sig_name
                    )
            axes[i,0].legend(frameon=False, loc='best')
            axes[i,0].set_xscale('log' if psf.log_x(sweep) else 'linear')
            axes[i,0].set_yscale('log' if psf.log_y(sweep) and not dB else 'linear')
            axes[i,0].xaxis.set_major_formatter(x_formatter)
            axes[i,0].yaxis.set_major_formatter(y_formatters[units])
        if title:
            plt.suptitle(title)
        if svg_file:
            plt.savefig(svg_file)
        else:
            plt.show()
    except Error as e:
        e.terminate()
    except KeyboardInterrupt as e:
        done()

# get_argv() {{{1
def get_argv():
    argv = sys.argv[1:]
    if argv:
        # save the command line arguments for next time
        try:
            with open(saved_arguments_filename, 'w') as f:
                args = [a for a in argv if a not in ['-c', '--no-cache']]
                f.write('\n'.join(args))
        except OSError as e:
            warn(os_error(e))
    else:
        # command line arguments not give, reuse previous ones
        try:
            with open(saved_arguments_filename) as f:
                argv = f.read().split('\n')
            display(f'Using command:', ' '.join(argv))
        except OSError:
            done()
    return argv

# get_psf_filename() {{{1
def get_psf_filename(psf_file):
    if not psf_file:
        try:
            with open(saved_psf_file_filename) as f:
                psf_file = f.read().strip()
            display(f'Using {psf_file}.')
        except OSError:
            fatal('missing psf file name.')
    try:
        with open(saved_psf_file_filename, 'w') as f:
            f.write(psf_file)
    except OSError as e:
        warn(os_error(e))
    return psf_file

# in_args() {{{1
def expand_args(signals, args):
    # special case args that contain -, they are considered differential signals
    # they should not include glob chars (*, ?)
    selected = set(a for a in args if '-' in a)
    for arg in args:
        selected.update(fnmatch.filter(signals, arg))
    return sorted(selected)
