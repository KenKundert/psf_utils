#!/usr/bin/env python3
# encoding: utf8

from psf_utils import PSF
from inform import Error, display
from pytest import raises, approx


def test_ac_lin():
    try:
        psf = PSF('samples/pnoise.raw/aclin.ac')
        sweep = psf.get_sweep()
        assert sweep.name == 'freq', 'sweep'
        assert sweep.units == 'Hz', 'sweep'
        assert len(sweep.abscissa) == 1001, 'sweep'
        assert isinstance(sweep.abscissa[0], float), 'sweep'

        signals = {
            'iRESref:p': ('A', 'complex double'),
            'iRESva:p':  ('A', 'complex double'),
            'noiref':    ('V', 'complex double'),
            'noiva':     ('V', 'complex double'),
            'top':       ('V', 'complex double'),
            'topref':    ('V', 'complex double'),
            'topva':     ('V', 'complex double'),
            'VTOP:p':    ('A', 'complex double'),
        }
        for signal in psf.all_signals():
            name = signal.name
            assert name in signals, signal.name
            units, kind = signals.pop(name)
            assert units == signal.units, signal.name
            assert kind == signal.type.kind, signal.name
            if name == 'top':
                assert isinstance(signal.ordinate[0], complex), signal.name
                assert len(signal.ordinate) == 1001
                assert max(signal.ordinate) == 1
                assert min(signal.ordinate) == 1
        assert not signals
    except Error as e:
        e.terminate()


def test_ac_log():
    try:
        psf = PSF('samples/pnoise.raw/aclog.ac')
        sweep = psf.get_sweep()
        assert sweep.name == 'freq', 'sweep'
        assert sweep.units == 'Hz', 'sweep'
        assert len(sweep.abscissa) == 61, 'sweep'
        assert isinstance(sweep.abscissa[0], float), 'sweep'

        signals = {
            'iRESref:p': ('A', 'complex double'),
            'iRESva:p':  ('A', 'complex double'),
            'noiref':    ('V', 'complex double'),
            'noiva':     ('V', 'complex double'),
            'top':       ('V', 'complex double'),
            'topref':    ('V', 'complex double'),
            'topva':     ('V', 'complex double'),
            'VTOP:p':    ('A', 'complex double'),
        }
        for signal in psf.all_signals():
            name = signal.name
            assert name in signals, signal.name
            units, kind = signals.pop(name)
            assert units == signal.units, signal.name
            assert kind == signal.type.kind, signal.name
            if name == 'top':
                assert isinstance(signal.ordinate[0], complex), signal.name
                assert len(signal.ordinate) == 61
                assert max(signal.ordinate) == 1
                assert min(signal.ordinate) == 1
        assert not signals
    except Error as e:
        e.terminate()


def test_noise():
    psf = PSF('samples/pnoise.raw/noiref.noise')
    sweep = psf.get_sweep()
    assert sweep.name == 'freq', 'sweep'
    assert sweep.units == 'Hz', 'sweep'
    assert len(sweep.abscissa) == 121, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'

    signals = {
        'RESref:fn':      ('V^2/Hz', 'float double'),
        'RESref:rn':      ('V^2/Hz', 'float double'),
        'RESref:total':   ('V^2/Hz', 'float double'),
        'RESva:flicker':  ('V^2/Hz', 'float double'),
        'RESva:thermal':  ('V^2/Hz', 'float double'),
        'RESva:total':    ('V^2/Hz', 'float double'),
        'Rref:rn':        ('V^2/Hz', 'float double'),
        'Rref:total':     ('V^2/Hz', 'float double'),
        'Rva:rn':         ('V^2/Hz', 'float double'),
        'Rva:total':      ('V^2/Hz', 'float double'),
        'out':            ('V/sqrt(Hz)', 'float double'),
    }
    for signal in psf.all_signals():
        name = signal.name
        assert name in signals, signal.name
        units, kind = signals.pop(name)
        assert units == signal.units, signal.name
        assert kind == signal.type.kind, signal.name
        if name == 'out':
            assert isinstance(signal.ordinate[0], float), signal.name
            assert len(signal.ordinate) == 121
            assert max(signal.ordinate) <= 6e-06
            assert min(signal.ordinate) >= 3e-10
    assert not signals


def test_pnoise():
    psf = PSF('samples/pnoise.raw/pnoiref.pnoise')
    sweep = psf.get_sweep()
    assert sweep.name == 'freq', 'sweep'
    assert sweep.units == 'Hz', 'sweep'
    assert len(sweep.abscissa) == 121, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'

    signals = {
        'RESref:fn':      ('V^2/Hz', 'float double'),
        'RESref:rn':      ('V^2/Hz', 'float double'),
        'RESref:total':   ('V^2/Hz', 'float double'),
        'RESva:flicker':  ('V^2/Hz', 'float double'),
        'RESva:thermal':  ('V^2/Hz', 'float double'),
        'RESva:total':    ('V^2/Hz', 'float double'),
        'Rref:rn':        ('V^2/Hz', 'float double'),
        'Rref:total':     ('V^2/Hz', 'float double'),
        'Rva:rn':         ('V^2/Hz', 'float double'),
        'Rva:total':      ('V^2/Hz', 'float double'),
        'out':            ('V/sqrt(Hz)', 'float double'),
    }
    for signal in psf.all_signals():
        name = signal.name
        assert name in signals, signal.name
        units, kind = signals.pop(name)
        assert units == signal.units, signal.name
        assert kind == signal.type.kind, signal.name
        if name == 'out':
            assert isinstance(signal.ordinate[0], float), signal.name
            assert len(signal.ordinate) == 121
            assert max(signal.ordinate) <= 10e-09
            assert min(signal.ordinate) >= 3e-10
    assert not signals


def test_pss_td():
    psf = PSF('samples/pnoise.raw/pss.td.pss')
    sweep = psf.get_sweep()
    assert sweep.name == 'time', 'sweep'
    assert sweep.units == 's', 'sweep'
    assert len(sweep.abscissa) == 1601, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'

    signals = {
        'VTOP:p':    ('A', 'float double'),
        'iRESref:p': ('A', 'float double'),
        'iRESva:p':  ('A', 'float double'),
        'noiref':    ('V', 'float double'),
        'noiva':     ('V', 'float double'),
        'top':       ('V', 'float double'),
        'topref':    ('V', 'float double'),
        'topva':     ('V', 'float double'),
    }
    for signal in psf.all_signals():
        name = signal.name
        assert name in signals, signal.name
        units, kind = signals.pop(name)
        assert units == signal.units, signal.name
        assert kind == signal.type.kind, signal.name
        if name == 'top':
            assert isinstance(signal.ordinate[0], float), signal.name
            assert len(signal.ordinate) == 1601
            assert max(signal.ordinate) <= 0.1
            assert min(signal.ordinate) >= -0.1
    assert not signals


def test_joop_banaan_tran():
    # a variant of the psf file format adds a unit property to the trace
    # definitions, this test assures that works.
    psf = PSF('samples/joop-banaan.tran')
    sweep = psf.get_sweep()
    assert sweep.name == 'time', 'sweep'
    assert sweep.units == 's', 'sweep'
    assert len(sweep.abscissa) == 55, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'

    signals = {
        'I2.comp_out_pre':    ('V', 'float double'),
        'I2.diff_cm':         ('V', 'float double'),
        'I2.diff_out_left':   ('V', 'float double'),
        'I2.diff_out_right':  ('V', 'float double'),
        'I2.pup2':            ('V', 'float double'),
        'I2.pup_b':           ('V', 'float double'),
        'V1:p':               ('A', 'float double'),
        'ibias':              ('V', 'float double'),
        'out':                ('V', 'float double'),
        'pup':                ('V', 'float double'),
        'vinp':               ('V', 'float double'),
        'vref_o':             ('V', 'float double'),
    }

    for signal in psf.all_signals():
        name = signal.name
        assert name in signals, signal.name
        units, kind = signals.pop(name)
        assert units == signal.units, signal.name
        assert kind == signal.type.kind, signal.name
        if name == 'top':
            assert isinstance(signal.ordinate[0], float), signal.name
            assert len(signal.ordinate) == 1601
            assert max(signal.ordinate) <= 0.1
            assert min(signal.ordinate) >= -0.1
    assert not signals

def test_joop_banaan_dc():
    psf = PSF('samples/joop-banaan.dc')
    sweep = psf.get_sweep()
    assert sweep == None, 'sweep'

    signals = {
        'I2.Idiffpair:in':    ('A', 'float double', 4.767791259200037e-08),
        'I2.comp_out_pre':    ('V', 'float double', 1.106383385957654e-06),
        'I2.diff_cm':         ('V', 'float double', 8.761644386176266e-04),
        'I2.diff_out_left':   ('V', 'float double', 7.998743518479743e-01),
        'I2.diff_out_right':  ('V', 'float double', 7.998743518480765e-01),
        'I2.pup2':            ('V', 'float double', 2.795768876173348e-07),
        'I2.pup_b':           ('V', 'float double', 7.999982644672001e-01),
        'Vsupply800m:p':      ('A', 'float double', -1.050027794352513e-06),
        'ibias':              ('V', 'float double', 3.588155366237979e-01),
        'out':                ('V', 'float double', 1.737370212928399e-07),
        'pup':                ('V', 'float double', 0.000000000000000e+00),
        'vinp':               ('V', 'float double', 2.000000000000000e-01),
        'vref_o':             ('V', 'float double', 2.000000000000000e-01),
    }

    for signal in psf.all_signals():
        name = signal.name
        assert name in signals, signal.name
        units, kind, expected = signals.pop(name)
        assert units == signal.units, signal.name
        assert kind == signal.type.kind, signal.name
        assert isinstance(signal.ordinate, float), signal.name
        assert signal.ordinate <= expected + 1e12
        assert signal.ordinate >= expected - 1e12
    assert not signals


if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.
    from inform import Error

    defined = dict(globals())
    for k, v in defined.items():
        try:
            if callable(v) and k.startswith('test_'):
                print()
                print('Calling:', k)
                print((len(k)+9)*'=')
                v()
        except Error as e:
            e.report()
