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
    -M, --mark-points             place marker on each point
    -P, --just-points             do not connect points with lines (implies -M)

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

If the dataset is for a DC operating point, the values are scalars rather than
waveforms and so are printed rather than plotted.
"""


# Imports {{{1
from .psf import PSF, Quantity
from docopt import docopt
import fnmatch
from inform import (
    Error, display, done, fatal, os_error, plural, warn
)
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import warnings
import sys

# Globals {{{1
axis_prec = 9  # can request many digits as unneeded digits are not shown
cursor_prec = 9
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
saved_arguments_filename = '.psf_plot_args'
operators = '+ - * /'.split()
signal_kinds = dict(V='V', A='I', s='t', Hz='f')


# Utilities {{{1
# get_argv() {{{3
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
        linestyle = '' if cmdline['--just-points'] else '-'
        marker = '.' if cmdline['--mark-points'] or cmdline['--just-points'] else ''

        # Open PSF file {{{2
        psf = PSF(psf_file, sep=':', use_cache=use_cache)
        sweep = psf.get_sweep()
        to_plot = expand_args(psf.signals.keys(), args)

        # x_name = sweep.name
        if not sweep:
            with Quantity.prefs(map_sf = Quantity.map_sf_to_greek, prec = print_prec):
                to_print = []
                width = 0
                for arg in to_plot:
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
                        y_data = Quantity(psig.ordinate - nsig.ordinate, units)
                        name = f'{access}({psig.name},{nsig.name})'
                    else:
                        sig = psf.get_signal(arg)
                        access = sig.access
                        name = f'{access}({sig.name})'
                        y_data = sig.ordinate
                    to_print.append((name, y_data))
                    width = max(width, len(name))
                for name, y_data in to_print:
                    display(f'{name:>{width+4}} = {y_data}')
                return

        x_units = sweep.units
        x_data = sweep.abscissa
        x_formatter = FuncFormatter(
            lambda v, p: Quantity(v, x_units).render()
        )

        # Process arguments {{{2
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
            if units == 'Unitless':
                units = ''
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
            u: FuncFormatter(
                lambda v, p, u=u: str(Quantity(v, psf.units_to_unicode(u)))
            )
            for u in y_units
        }

        xy_formatters = {}
        x_kind = signal_kinds.get(x_units, x_units)
        for u in y_units:
            y_kind = signal_kinds.get(x_units, u)
            xy_label = f"{x_kind} = {{x}},  {y_kind} = {{y}}"
            units = psf.units_to_unicode(u)
            xy_formatters[u] = lambda x, y: xy_label.format(
                x = Quantity(x, x_units).render(prec=cursor_prec),
                y = Quantity(y, units).render(prec=cursor_prec)
            )

        # Generate the plot {{{2
        if svg_file:
            matplotlib.use('SVG')
        figure, axes = plt.subplots(len(y_units), 1, sharex=True, squeeze=False)
        for i, units in enumerate(y_units):
            for sig_name, y_data, sig_units in waves:
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
            axes[i, 0].set_yscale('log' if psf.log_y(sweep) and not dB else 'linear')
            axes[i, 0].xaxis.set_major_formatter(x_formatter)
            axes[i, 0].yaxis.set_major_formatter(y_formatters[units])
            axes[i, 0].format_coord = xy_formatters[units]
        if title:
            plt.suptitle(title)
        if svg_file:
            plt.savefig(svg_file)
        else:
            plt.show()
    except Error as e:
        e.terminate()
    except KeyboardInterrupt:
        done()
