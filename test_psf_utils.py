#!/usr/bin/env python3
# encoding: utf8

from psf_utils import PSF
from inform import Error, display
from pytest import raises, approx


def test_ac_lin():
    psf = PSF('samples/pnoise.raw/aclin.ac')
    sweep = psf.get_sweep()
    assert sweep.name == 'freq', 'sweep'
    assert sweep.units == 'Hz', 'sweep'
    assert len(sweep.abscissa) == 1001, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'
    assert psf.log_x() == False
    assert psf.log_y() == False
    assert psf.log_x(sweep) == False
    assert psf.log_y(sweep) == False

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


def test_ac_log():
    psf = PSF('samples/pnoise.raw/aclog.ac')
    sweep = psf.get_sweep()
    assert sweep.name == 'freq', 'sweep'
    assert sweep.units == 'Hz', 'sweep'
    assert len(sweep.abscissa) == 61, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'
    assert psf.log_x() == True
    assert psf.log_y() == True
    assert psf.log_x(sweep) == True
    assert psf.log_y(sweep) == True

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
    signal = psf.get_signal('Rref:total')
    units = signal.units
    assert psf.units_to_unicode(units) == 'V²/Hz', signal.name
    assert psf.units_to_latex(units) == 'V^2/Hz', signal.name
    signal = psf.get_signal('out')
    units = signal.units
    assert psf.units_to_unicode(units) == 'V/√Hz', signal.name
    assert psf.units_to_latex(units) == 'V/sqrt(Hz)', signal.name


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


def test_fracpole_dc():
    psf = PSF('samples/fracpole.dc')
    sweep = psf.get_sweep()
    assert sweep == None, 'sweep'

    signals = {
        'z6':    ('V', 'float double', 0.00000),
        'z2':    ('V', 'float double', 0.00000),
        'FP6.1': ('V', 'float double', 0.00000),
        'FP6.2': ('V', 'float double', 0.00000),
        'FP6.3': ('V', 'float double', 0.00000),
        'FP6.4': ('V', 'float double', 0.00000),
        'FP6.5': ('V', 'float double', 0.00000),
        'FP2.1': ('V', 'float double', 0.00000),
        'FP2.2': ('V', 'float double', 0.00000),
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


def test_fracpole_ac():
    psf = PSF('samples/fracpole.ac')
    sweep = psf.get_sweep()
    assert sweep.name == 'freq', 'sweep'
    assert sweep.units == 'Hz', 'sweep'
    assert len(sweep.abscissa) == 121, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'

    signals = {
        'z6':    ('V', 'complex double'),
        'z2':    ('V', 'complex double'),
        'FP6.1': ('V', 'complex double'),
        'FP6.2': ('V', 'complex double'),
        'FP6.3': ('V', 'complex double'),
        'FP6.4': ('V', 'complex double'),
        'FP6.5': ('V', 'complex double'),
        'FP2.1': ('V', 'complex double'),
        'FP2.2': ('V', 'complex double'),
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


def test_fracpole_ac_again():
    # run exact same test again, this time it should use the cache
    # also, use get_signal interface rather than all_signals
    psf = PSF('samples/fracpole.ac')
    sweep = psf.get_sweep()
    assert sweep.name == 'freq', 'sweep'
    assert sweep.units == 'Hz', 'sweep'
    assert len(sweep.abscissa) == 121, 'sweep'
    assert isinstance(sweep.abscissa[0], float), 'sweep'

    signals = {
        'z6':    ('V', 'complex double'),
        'z2':    ('V', 'complex double'),
        'FP6.1': ('V', 'complex double'),
        'FP6.2': ('V', 'complex double'),
        'FP6.3': ('V', 'complex double'),
        'FP6.4': ('V', 'complex double'),
        'FP6.5': ('V', 'complex double'),
        'FP2.1': ('V', 'complex double'),
        'FP2.2': ('V', 'complex double'),
    }
    for name in signals:
        signal = psf.get_signal(name)
        assert name == signal.name, signal.name
        units, kind = signals[name]
        assert units == signal.units, signal.name
        assert kind == signal.type.kind, signal.name
        if name == 'top':
            assert isinstance(signal.ordinate[0], complex), signal.name
            assert len(signal.ordinate) == 1001
            assert max(signal.ordinate) == 1
            assert min(signal.ordinate) == 1


def test_dc_oppoint():
    psf = PSF('samples/dcOpInfo.info.psfascii')
    signals = """
        NM0.beff        A/V²  real
        NM0.betaeff     A/V²  real
        NM0.cbb         F     real
        NM0.cbd         F     real
        NM0.cbdbi       F     real
        NM0.cbg         F     real
        NM0.cbs         F     real
        NM0.cbsbi       F     real
        NM0.cdb         F     real
        NM0.cdd         F     real
        NM0.cddbi       F     real
        NM0.cdg         F     real
        NM0.cds         F     real
        NM0.cgb         F     real
        NM0.cgbovl      F     real
        NM0.cgd         F     real
        NM0.cgdbi       F     real
        NM0.cgdovl      F     real
        NM0.cgg         F     real
        NM0.cggbi       F     real
        NM0.cgs         F     real
        NM0.cgsbi       F     real
        NM0.cgsovl      F     real
        NM0.cjd         F     real
        NM0.cjs         F     real
        NM0.csb         F     real
        NM0.csd         F     real
        NM0.csg         F     real
        NM0.css         F     real
        NM0.cssbi       F     real
        NM0.ft          Hz    real
        NM0.fug         Hz    real
        NM0.gbd         S     real
        NM0.gbs         S     real
        NM0.gds         S     real
        NM0.gm          S     real
        NM0.gmb         S     real
        NM0.gmbs        S     real
        NM0.gmoverid    1/V   real
        NM0.i1          A     real
        NM0.i3          A     real
        NM0.i4          A     real
        NM0.ib          A     real
        NM0.ibd         A     real
        NM0.ibe         A     real
        NM0.ibs         A     real
        NM0.ibulk       A     real
        NM0.id          A     real
        NM0.idb         A     real
        NM0.ide         A     real
        NM0.ids         A     real
        NM0.ig          A     real
        NM0.igb         A     real
        NM0.igcd        A     real
        NM0.igcs        A     real
        NM0.igd         A     real
        NM0.ige         A     real
        NM0.igidl       A     real
        NM0.igisl       A     real
        NM0.igs         A     real
        NM0.is          A     real
        NM0.isb         A     real
        NM0.ise         A     real
        NM0.isub        A     real
        NM0.pwr         W     real
        NM0.qb          Coul  real
        NM0.qbd         Coul  real
        NM0.qbi         Coul  real
        NM0.qbs         Coul  real
        NM0.qd          Coul  real
        NM0.qdi         Coul  real
        NM0.qg          Coul  real
        NM0.qgi         Coul  real
        NM0.qinv        Coul  real
        NM0.qsi         Coul  real
        NM0.qsrco       Coul  real
        NM0.region            integer
        NM0.reversed          integer
        NM0.ron         Ω     real
        NM0.rout        Ω     real
        NM0.self_gain         real
        NM0.tk          K     real
        NM0.type              integer
        NM0.ueff              real
        NM0.vbs         V     real
        NM0.vdb         V     real
        NM0.vds         V     real
        NM0.vdsat       V     real
        NM0.vdsat_marg  V     real
        NM0.vdss        V     real
        NM0.vearly      V     real
        NM0.vfbeff      V     real
        NM0.vgb         V     real
        NM0.vgd         V     real
        NM0.vgs         V     real
        NM0.vgsteff     V     real
        NM0.vgt         V     real
        NM0.vsat_marg   V     real
        NM0.vsb         V     real
        NM0.vth         V     real
        NM0.vth_drive   V     real
        V0.i            A     real
        V0.pwr          W     real
        V0.v            V     real
        V1.i            A     real
        V1.pwr          W     real
        V1.v            V     real
    """.strip()
    for line in signals.splitlines():
        components = line.split()
        if len(components) == 3:
            name, units, kind = components
        else:
            name, kind = components
            units = ''
        type_maps = dict(
            real = 'float double',
            complex = 'complex double',
            integer = 'int byte',
        )
        signal = psf.get_signal(name)
        assert name == signal.name, signal.name
        assert units == PSF.units_to_unicode(signal.units), signal.name
        assert type_maps[kind] == signal.type.kind, signal.name


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
