"""
Read PSF File
"""

# Imports {{{1
from .parse import ParsePSF, ParseError
from inform import Error, Info, log, join, os_error
from shlib import to_path
import numpy as np
from quantiphy import Quantity
try:
    import cPickle as pickle
except ImportError:
    import pickle
import re


# Utilities {{{1
class Signal(Info):
    pass


class UnknownSignal(Error):
    template = 'unknown signal: {}.'


unicode_unit_maps = [
    (r'sqrt\(([^)]+)\)', r'√\1'),
    (r'\^2', r'²'),
]


def unicode_units(u):
    for s, r in unicode_unit_maps:
        u = re.sub(s, r, u)
    return u


# PSF class {{{1
class PSF:
    """
    Read an ASCII PSF file

    filename (str or Path):
        Path to ASCII PSF file.
    sep (str):
        Join string to use when converting composite names into a single name.
    use_cache (bool):
        If True, a cached version of the data is used if it exists rather than
        the original PSF file, but only if the cache is newer than the PSF file.
        This can substantially reduced the time required to access the data.
    update_cache (bool):
        If True, a cached version of the data is updated if it does not exist or
        is out-of-date.
    """

    def __init__(self, filename, sep=':', use_cache=True, update_cache=True):
        psf_filepath = to_path(filename)
        cache_filepath = psf_filepath.with_suffix(psf_filepath.suffix + '.cache')

        # read cache if desired and current
        if use_cache:
            try:
                if cache_filepath.stat().st_mtime > psf_filepath.stat().st_mtime:
                    self._read_cache(cache_filepath)
                    return
            except OSError as e:
                log(os_error(e))
            except Exception as e:
                log(e)

        # open and parse PSF file
        parser = ParsePSF()
        try:
            content = psf_filepath.read_text()
            sections = parser.parse(filename, content)
        except ParseError as e:
            raise Error(str(e))
        except OSError as e:
            raise Error(os_error(e))
        except UnicodeError as e:
            raise Error(
                e,
                culprit = psf_filepath,
                codicil = join(
                    'This is likely a binary PSF file,',
                    'psf_utils only supports ASCII PSF files.',
                    '\nUse `psf {0!s} {0!s}.ascii` to convert.'.format(psf_filepath),
                )
            )
        meta, types, sweeps, traces, values = sections
        self.meta = meta
        self.types = types
        self.sweeps = sweeps
        self.traces = traces

        # add values to sweeps
        if sweeps:
            for sweep in sweeps:
                n = sweep.name
                sweep.abscissa = np.array(values[n].values)

        # process signals
        # 1. convert to numpy and delete the original list
        # 2. convert to Signal class
        # 3. create signals dictionary
        signals = {}
        if traces:
            for trace in traces:
                name = trace.name
                type = types[trace.type]
                vals = values[name].values
                if type.struct:
                    for i, v in enumerate(type.struct.types.items()):
                        n, t = v
                        names = (name, n)
                        joined_names = sep.join(names)
                        if 'complex' in t.kind:
                            ordinate = np.array([complex(*v[i]) for v in vals])
                        else:
                            ordinate = np.array(vals)
                        signal = Signal(
                            name = joined_names,
                            names = names,
                            ordinate = ordinate,
                            type = t,
                            access = t.name,
                            units = t.units,
                            meta = meta,
                        )
                        signals[joined_names] = signal
                else:
                    names = (name,)
                    if 'complex' in type.kind:
                        ordinate = np.array([complex(*v) for v in vals])
                    else:
                        ordinate = np.array(vals)
                    signal = Signal(
                        name = name,
                        names = names,
                        ordinate = ordinate,
                        type = type,
                        access = type.name,
                        units = type.units,
                        meta = meta,
                    )
                    signals[name] = signal
                del values[name]
        else:
            # no traces, this should be a DC op-point analysis dataset
            for name, value in values.items():
                names = (name,)
                type = types[value.type]
                if 'complex' in type.kind:
                    # these should be DC values, so complex is not needed
                    raise NotImplementedError
                assert len(value.values) == 1
                signal = Signal(
                    name = name,
                    names = names,
                    ordinate = Quantity(value.values[0], type.units),
                    type = type,
                    access = type.name,
                    units = type.units,
                    meta = meta,
                )
                signals[name] = signal
        self.signals = signals

        if update_cache:
            self._write_cache(cache_filepath)

    def get_sweep(self, index=0):
        """
        Get Sweep

        index (int):
            PSF allows multiple sweeps (abscissas). You can use this argument to
            select the one you want. The default is 0.
        """
        if self.sweeps:
            return self.sweeps[index]

    def get_signal(self, name):
        """
        Get Signal

        name (string):
            Name of signal return.

        Raises UnknownSignal (subclass of Error) if the name given does not
        correspond to a known signal.
        """
        try:
            return self.signals[name]
        except KeyError:
            raise UnknownSignal(name, choices=self.signals.keys())

    def all_signals(self):
        """
        All Signals

        Iterates through all signals.
        """
        for signal in self.signals.values():
            yield signal

    def log_x(self, sweep=None):
        """
        Log X

        True if PSF is recommending a logarithmic x-axis.
        """
        if not sweep:
            sweep = self.get_sweep()
        return sweep.grid == 3

    def log_y(self, sweep=None):
        """
        Log Y

        True if PSF is recommending a logarithmic y-axis.
        """
        if not sweep:
            sweep = self.get_sweep()
        return sweep.grid == 3

    @staticmethod
    def units_to_unicode(units):
        """
        Transform ASCII units to Unicode

        units (str):
            The units to transform.
        """
        return unicode_units(units)

    @staticmethod
    def units_to_latex(units):
        """
        Transform ASCII units to Latex

        Note: this function is not yet implemented.

        units (str):
            The units to transform.
        """
        return units

    def _read_cache(self, cache_filepath):
        with open(cache_filepath, 'rb') as f:
            self.__dict__ = pickle.load(f)

    def _write_cache(self, cache_filepath):
        with open(cache_filepath, 'wb') as f:
            pickle.dump(self.__dict__, f, pickle.HIGHEST_PROTOCOL)
