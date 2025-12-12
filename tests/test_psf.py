# encoding: utf8

# Imports {{{1
from parametrize_from_file import parametrize, Namespace
import pytest
from functools import partial
from voluptuous import Schema, Optional, Required
from psf_utils import PSF
from pathlib import Path
from shlib import Run, rm
import math


# Utilities {{{1
def name_from_dict_keys(cases):
    return [{**v, 'name': k} for k,v in cases.items()]

# Globals {{{1
type_maps = {
    'float double': float,
    'float single': float,
    'complex double': complex,
    'complex single': complex,
    'int byte': int,
    'int long': int,
    'string *': str,
}
parametrize_from_file = partial(parametrize, preprocess=name_from_dict_keys)
with_quantiphy = Namespace('from quantiphy import Quantity')

# Schemas {{{1
# Schema for API test cases
api_test_schema = Schema({
    Required('name'): str,
    Required('path'): str,
    Required('expected'): dict(sweep={str:str}, signals={str:{str:str}}),
})

# Schema for utilities test cases
utils_test_schema = Schema({
    Required('name'): str,
    Required('command'): str,
    Required('psf_file'): str,
    Optional('arguments', default=''): str,
    Optional('expected', default=''): str,
})

# run_api_test {{{1
def run_api_test(test_name, psf_file, expected):
    # open the PSF file
    try:
        psf = PSF(psf_file)
    except KeyError as e:
        pytest.fail(
            f"in {test_name}\nERROR: Failed to load PSF file. KeyError: {e}\n" 
            f"This usually means a signal name in the TRACE section (e.g. 'I48.LOGIC_OUT<3>')\n" 
            f"does not match any signal found in the VALUE section.\n" 
            f"If this is the 'bus_chevrons_tran' test, check if escaped characters are being handled correctly."
        )

    sweep = psf.get_sweep()
    test_desc = f'in {test_name}'

    # check sweep
    if 'sweep' in expected:

        # check sweep name
        assert sweep.name == expected['sweep']['name'], test_desc

        # check sweep units
        assert sweep.units == expected['sweep']['units'], test_desc

        # check sweep length
        num_points = int(expected['sweep']['length'])
        assert len(sweep.abscissa) == num_points, test_desc

        # check sweep type
        assert psf.types['sweep'].kind == expected['sweep']['type'], test_desc
        assert isinstance(sweep.abscissa[0], type_maps[expected['sweep']['type']]), test_desc

        # check grid
        expected_grid = expected['sweep']['grid']
        if expected_grid == 'linear':
            assert sweep.grid == 1, test_desc
            is_log = False
        elif expected_grid == 'logarithmic':
            assert sweep.grid == 3, test_desc
            is_log = True
        elif expected_grid == 'n/a':
            assert sweep.grid is None, test_desc
            is_log = None
        else:
            raise NotImplementedError
        if is_log is not None:
            assert psf.log_x() == is_log, test_desc
            assert psf.log_y() == is_log, test_desc
            assert psf.log_x(sweep) == is_log, test_desc
            assert psf.log_y(sweep) == is_log, test_desc
    else:
        assert sweep is None, test_desc

    remaining = expected['signals'].copy()
    for signal in psf.all_signals():
        name = signal.name
        test_desc = f'in {test_name} on {name}'
        print(f"NAME: {test_desc}")

        # check that this is a known signal
        # check that this is a known signal
        if name not in remaining:
            pytest.fail(
                f"{test_desc}\nERROR: Found unexpected signal '{name}' in the PSF file.\n"
                f"Expected signals: {list(remaining.keys())}\n"
                f"This failure means the PSF reader found a signal that wasn't in the test expectation.\n"
                f"If this is the 'bus_chevrons_tran' test, check if 'I48.LOGIC_OUT<3>' is being parsed correctly (e.g. unescaped)."
            )

        # check get_signal()
        sig = psf.get_signal(name)
        assert signal == sig, test_desc

        # check signal units
        signal_attributes = remaining.pop(name)
        if 'units' in signal_attributes:
            assert signal.units == signal_attributes['units'], test_desc
        else:
            assert not signal.units

        # check signal type
        assert signal.type.kind == signal_attributes['type'], test_desc
        expected_type = type_maps[signal_attributes['type']]

        # check signal length
        if sweep:
            assert len(signal.ordinate) == num_points
            assert isinstance(signal.ordinate[0], expected_type), test_desc

        # check signal values
        if 'max' in signal_attributes:
            expected_max = expected_type(signal_attributes['max'].replace(' ',''))
            assert max(signal.ordinate) <= expected_max, test_desc
        if 'min' in signal_attributes:
            expected_min = expected_type(signal_attributes['min'].replace(' ',''))
            assert min(signal.ordinate) >= expected_min, test_desc
        if 'value' in signal_attributes:
            expected_value = expected_type(signal_attributes['value'])
            if isinstance(signal.ordinate, float) and math.isnan(expected_value):
                assert math.isnan(signal.ordinate)
            else:
                assert signal.ordinate == pytest.approx(expected_value, abs=1e-12)
            if 'units' in signal_attributes:
                assert signal.units == signal_attributes['units']

    # assure that all signals were checked
    assert not remaining

# test_api {{{1
@parametrize_from_file(schema=api_test_schema)
def test_api(name, path, expected):
    # fix up the path
    test_dir = Path(__file__).parent
    psf_file = test_dir/path

    # clean any existing cache
    cache_file = Path(str(psf_file) + '.cache')
    rm(cache_file)

    # run test without cache
    assert not cache_file.exists()
    run_api_test(name, psf_file, expected)

    # run test again, this time the data should be cached
    print(str(cache_file))
    assert cache_file.exists()
    run_api_test(name, psf_file, expected)

# test_utils {{{1
@parametrize_from_file(schema=utils_test_schema)
def test_utils(name, command, psf_file, arguments, expected):
    # fix up the paths
    test_dir = Path(__file__).parent
    root_dir = test_dir.parent
    psf_file = root_dir/psf_file
    command = root_dir/command
    svg_file = test_dir/'test_psf.svg'

    # replace @ with svg_file in arguments
    arguments = arguments.replace('@', str(svg_file))

    # run test
    cmd = [command, '-f', psf_file] + arguments.split()
    process = Run(cmd, modes='sOEW')
    assert process.stdout.rstrip() == expected.rstrip(), name
    assert process.stderr == '', name

    # remove svg_file if it was created
    rm(svg_file)

# Error Handling Tests {{{1
def test_binary_psf_error():
    """Test that binary PSF files raise appropriate error"""
    test_dir = Path(__file__).parent
    binary_file = test_dir / "binary_test.psf"

    # Create a binary file
    binary_file.write_bytes(b'\x00\xff\xfe\xfd' * 100)

    try:
        with pytest.raises(Exception) as exc_info:
            PSF(binary_file)
        # Should raise Error about binary PSF
        assert "binary PSF" in str(exc_info.value) or "UnicodeDecodeError" in str(type(exc_info.value))
    finally:
        # Clean up
        rm(binary_file)

def test_missing_file_error():
    """Test that missing files raise appropriate error"""
    from inform import Error
    with pytest.raises(Error):
        PSF("nonexistent_file_12345.psf")

def test_malformed_psf_error():
    """Test that malformed PSF files raise appropriate error"""
    from inform import Error
    test_dir = Path(__file__).parent
    malformed_file = test_dir / "malformed_test.psf"

    # Create a malformed PSF file
    malformed_file.write_text("HEADER\nGARBAGE DATA!!!\nMORE GARBAGE\n")

    try:
        with pytest.raises(Error):
            PSF(malformed_file)
    finally:
        # Clean up
        rm(malformed_file)

def test_corrupted_cache():
    """Test that corrupted cache files are handled gracefully"""
    test_dir = Path(__file__).parent
    psf_file = test_dir / "../samples/pnoise.raw/aclin.ac"
    cache_file = psf_file.with_suffix(".ac.cache")

    # Remove existing cache
    rm(cache_file)

    # Create corrupted cache
    cache_file.write_bytes(b"corrupted cache data\x00\xff")

    try:
        # Should fall back to parsing PSF file
        psf = PSF(psf_file)
        assert psf is not None
        assert psf.get_sweep() is not None
    finally:
        # Clean up
        rm(cache_file)

# Static Method Tests {{{1
def test_unknown_signal():
    """Test that accessing unknown signal raises UnknownSignal"""
    from psf_utils.psf import UnknownSignal
    test_dir = Path(__file__).parent
    psf_file = test_dir / "../samples/pnoise.raw/aclin.ac"

    # Clean cache
    cache_file = psf_file.with_suffix(".ac.cache")
    rm(cache_file)

    try:
        psf = PSF(psf_file)
        with pytest.raises(UnknownSignal):
            psf.get_signal("nonexistent_signal_xyz_12345")
    finally:
        rm(cache_file)

def test_units_to_unicode():
    """Test units conversion to unicode"""
    assert PSF.units_to_unicode("Ohm") == "Ω"
    assert PSF.units_to_unicode("V^2") == "V²"
    assert PSF.units_to_unicode("sqrt(Hz)") == "√Hz"
    assert PSF.units_to_unicode("R") == "Ω"  # Resistance
    assert PSF.units_to_unicode("") == ""
    assert PSF.units_to_unicode(None) == ""

def test_units_to_latex():
    """Test units conversion to latex (not implemented)"""
    result = PSF.units_to_latex("V/A")
    # Currently returns input unchanged
    assert result == "V/A"
