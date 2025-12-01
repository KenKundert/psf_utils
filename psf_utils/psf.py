"""
Read PSF File
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
from .parse import ParsePSF, ParseError
from inform import Error, Info, join, log, os_error
from pathlib import Path
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


unicode_unit_maps = {
    r'sqrt\(([^)]+)\)': r'√\1',
    r'\^2': '²',
    r'\bOhm\b': 'Ω',

    # the following are not unicode units, however Spectre often messes these
    # up in the oppoint files.
    r'\bR\b': 'Ω',
    r'\bI\b': 'A',
    r'\bC\b': 'F',
    r'\bDeg\b': '°',
}


def unicode_units(u):
    if u:
        for s, r in unicode_unit_maps.items():
            u = re.sub(s, r, u)
    else:
        u = ''
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
        psf_filepath = Path(filename)
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
            
            # Hybrid approach: Try to separate header/types from values
            # We look for the VALUE section
            value_idx = content.find("\nVALUE")
            if value_idx == -1:
                value_idx = content.find("VALUE")
                
            if value_idx != -1:
                # We found VALUE section.
                # Let's see if we can fast-read it.
                
                # Check for GROUP in TRACE section before attempting fast read
                # The TRACE section is before VALUE.
                trace_idx = content.find("\nTRACE")
                if trace_idx == -1:
                    trace_idx = content.find("TRACE")
                
                has_group = False
                if trace_idx != -1 and trace_idx < value_idx:
                    trace_section = content[trace_idx:value_idx]
                    if "GROUP" in trace_section:
                        has_group = True
                
                fast_values = None
                fast_names = None
                
                if not has_group:
                    # Let's try to read the file as bytes for fast reading
                    with open(filename, 'rb') as f:
                        content_bytes = f.read()
                        
                    # Try fast read of values
                    fast_values, fast_names = self._fast_read_values(content_bytes)
                
                if fast_values is not None:
                    # Fast read successful!
                    # Now parse metadata.
                    
                    # Truncate content for parser
                    prefix = content[:value_idx]
                    dummy_content = prefix + "\nVALUE\n\"dummy_var_for_fast_read\" 0.0\nEND"
                    
                    sections = parser.parse(filename, dummy_content)
                    
                    # Now we have metadata.
                    # We need to inject our fast values into 'sections'.
                    # sections = (meta, types, sweeps, traces, values)
                    meta, types, sweeps, traces, values = sections
                    
                    # 'values' contains the dummy. We discard it.
                    values = {}
                    
                    # Re-construct values dict
                    class Value(Info):
                        pass
                    
                    for i, name in enumerate(fast_names):
                        # Handle escaped characters in names from fast reader
                        # The fast reader might return "I48.LOGIC_OUT\<3\>"
                        # But the parser (and traces) expects "I48.LOGIC_OUT<3>"
                        # We need to unescape backslashes
                        clean_name = name.replace('\\', '')
                        
                        # Extract column
                        col = fast_values[:, i]
                        # We wrap it in a Value object
                        # We flag it as 'fast_array' so __init__ knows
                        v_obj = Value(values=col, is_fast=True)
                        values[clean_name] = v_obj
                        
                    # Update sections
                    sections = (meta, types, sweeps, traces, values)
                    
                else:
                    # Fast read failed or skipped, fallback
                    sections = parser.parse(filename, content)
            else:
                # No VALUE section?
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
                # Check if it's a fast value
                val_obj = values[n]
                if getattr(val_obj, 'is_fast', False):
                    # It's already a numpy array
                    sweep.abscissa = val_obj.values
                else:
                    # Original logic
                    sweep.abscissa = np.array([v[0] for v in val_obj.values])

        # process signals
        # 1. convert to numpy and delete the original list
        # 2. convert to Signal class
        # 3. create signals dictionary
        signals = {}
        if traces:
            traces, groups = traces
            for trace in traces:
                name = trace.name
                type = types.get(trace.type, trace.type)
                
                val_obj = values[name]
                vals = val_obj.values
                is_fast = getattr(val_obj, 'is_fast', False)
                
                if type == 'GROUP':
                    group = {k: types.get(v, v) for k, v in groups[name].items()}
                    prefix = ''
                    get_value = lambda v, i: v[i]
                elif type.struct:
                    group = type.struct.types
                    prefix = name + ':'
                    get_value = lambda v, i: v[0][i]
                else:
                    group = {name: type}
                    prefix = ''
                    get_value = lambda v, i: v[i]
                for i, v in enumerate(group.items()):
                    n, t = v
                    joined_name = prefix + n
                    
                    if is_fast:
                        # If fast read, vals is already the numpy array for this signal
                        # And we assume fast read only handles simple scalar floats for now.
                        # So 'vals' IS the ordinate.
                        ordinate = vals
                    else:
                        if 'complex' in t.kind:
                            ordinate = np.array([complex(*get_value(v, i)) for v in vals])
                        else:
                            ordinate = np.array([get_value(v, i) for v in vals])
                            
                    signal = Signal(
                        name = joined_name,
                        ordinate = ordinate,
                        type = t,
                        access = t.name,
                        units = t.units,
                        # units = t.units if t.units else t.name,
                            # I think that terminal currents are misnamed
                            # they should be named "I" but they are named "A"
                            # and "A" is a type where no units are specified,
                            # so as a hack, use the name rather than
                            # go without units
                        meta = meta,
                    )
                    signals[joined_name] = signal
                del values[name]
        else:
            # no traces, this should be a DC op-point analysis dataset
            for name, value in values.items():
                # For DC analysis, fast read likely failed or we didn't use it
                is_fast = getattr(value, 'is_fast', False)
                if is_fast:
                     v = value.values[0] 
                else:
                    assert len(value.values) == 1
                    type = types[value.type]
                    if type.struct:
                        for t, v in zip(type.struct.types.values(), value.values[0][0]):
                            n = f'{name}.{t.name}'
                            if 'float' in t.kind:
                                v = Quantity(v, unicode_units(t.units))
                            elif 'complex' in t.kind:
                                v = complex(v[0], v[1])
                            signal = Signal(
                                name = n,
                                ordinate = v,
                                type = t,
                                units = t.units,
                                meta = meta,
                            )
                            signals[n] = signal
                    else:
                        if 'float' in type.kind:
                            v = Quantity(value.values[0][0], unicode_units(type.units))
                        elif 'complex' in type.kind:
                            v = complex(value.values[0][0], value.values[0][1])
                        else:
                            v = value.values[0]

                        signal = Signal(
                            name = name,
                            ordinate = v,
                            type = type,
                            access = type.name,
                            units = type.units,
                            meta = meta,
                        )
                        signals[name] = signal
        self.signals = signals

        if update_cache:
            self._write_cache(cache_filepath)

    def _fast_read_values(self, content_bytes):
        """
        Attempts to read the VALUE section using fast numpy parsing.
        Returns (values_array, names_list) if successful, or (None, None) if not.
        """
        try:
            # Find VALUE section
            idx = content_bytes.find(b"\nVALUE\n")
            if idx == -1:
                idx = content_bytes.find(b"VALUE\n")
                if idx == -1:
                    return None, None
                start_offset = idx + 6
            else:
                start_offset = idx + 7

            data_content = content_bytes[start_offset:]
            
            # We need to stop at END if it exists
            end_idx = data_content.rfind(b"\nEND")
            if end_idx != -1:
                data_content = data_content[:end_idx]
            
            tokens = data_content.split()

            if not tokens:
                return None, None

            # Identify signals
            first_name_bytes = tokens[0]
            cycle_len = 0
            for i in range(2, len(tokens), 2):
                if tokens[i] == first_name_bytes:
                    cycle_len = i // 2
                    break
            
            if cycle_len == 0:
                 return None, None

            names = [t.decode('utf-8').strip('"') for t in tokens[0:cycle_len*2:2]]
            
            total_tokens = len(tokens)
            num_rows = total_tokens // (2 * cycle_len)
            
            if num_rows == 0:
                return None, None
                
            tokens = tokens[:num_rows * 2 * cycle_len]
            
            try:
                values = np.array(tokens[1::2], dtype=float)
            except ValueError:
                return None, None
                
            data = values.reshape((num_rows, cycle_len))
            
            return data, names

        except Exception:
            return None, None

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
