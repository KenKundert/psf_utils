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
        assert signal.ordinate <= expected + 1e-12
        assert signal.ordinate >= expected - 1e-12
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
        assert signal.ordinate <= expected + 1e-12
        assert signal.ordinate >= expected - 1e-12
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
            real = ['float double'],
            complex = ['complex double'],
            integer = ['int byte', 'int long', 'int'],
        )
        signal = psf.get_signal(name)
        assert name == signal.name, signal.name
        assert units == PSF.units_to_unicode(signal.units), signal.name
        assert signal.type.kind in type_maps[kind], signal.name


def test_dan_zilla():
    # ignore backslashes in names
    psf = PSF('samples/dan-zilla.psfascii')
    signals = """
        Dout<0>           V  real  (65 points)
        Dout<10>          V  real  (65 points)
        Dout<11>          V  real  (65 points)
        Dout<1>           V  real  (65 points)
        Dout<2>           V  real  (65 points)
        Dout<3>           V  real  (65 points)
        Dout<4>           V  real  (65 points)
        Dout<5>           V  real  (65 points)
        Dout<6>           V  real  (65 points)
        Dout<7>           V  real  (65 points)
        Dout<8>           V  real  (65 points)
        Dout<9>           V  real  (65 points)
        I43.I0.net9       V  real  (65 points)
        I43.I2.net9       V  real  (65 points)
        I64.I2.net11      V  real  (65 points)
        I64.I3.net11      V  real  (65 points)
        I64.I5.net11      V  real  (65 points)
        I64.I6.net11      V  real  (65 points)
        I64.V0:p          A  real  (65 points)
        I64.net02         V  real  (65 points)
        I64.net03         V  real  (65 points)
        I64.net9          V  real  (65 points)
        I68.I0.net9       V  real  (65 points)
        I68.I1.net9       V  real  (65 points)
        I68.I10.net9      V  real  (65 points)
        I68.I11.net9      V  real  (65 points)
        I68.I12.net9      V  real  (65 points)
        I68.I13.net9      V  real  (65 points)
        I68.I14.net9      V  real  (65 points)
        I68.I15.net9      V  real  (65 points)
        I68.I16.net9      V  real  (65 points)
        I68.I17.net9      V  real  (65 points)
        I68.I2.net9       V  real  (65 points)
        I68.I3.net9       V  real  (65 points)
        I68.I30.net9      V  real  (65 points)
        I68.I31.net9      V  real  (65 points)
        I68.I32.net9      V  real  (65 points)
        I68.I33.net9      V  real  (65 points)
        I68.I4.net9       V  real  (65 points)
        I68.I5.net9       V  real  (65 points)
        I68.I6.net9       V  real  (65 points)
        I68.I7.net9       V  real  (65 points)
        I68.I8.net9       V  real  (65 points)
        I68.I9.net9       V  real  (65 points)
        I68.net1          V  real  (65 points)
        I68.net15         V  real  (65 points)
        I68.net16         V  real  (65 points)
        I68.net17         V  real  (65 points)
        I68.net18         V  real  (65 points)
        I68.net19         V  real  (65 points)
        I68.net2          V  real  (65 points)
        I68.net20         V  real  (65 points)
        I68.net21         V  real  (65 points)
        I68.net22         V  real  (65 points)
        I68.net23         V  real  (65 points)
        I70.I5<0>.net11   V  real  (65 points)
        I70.I5<10>.net11  V  real  (65 points)
        I70.I5<11>.net11  V  real  (65 points)
        I70.I5<1>.net11   V  real  (65 points)
        I70.I5<2>.net11   V  real  (65 points)
        I70.I5<3>.net11   V  real  (65 points)
        I70.I5<4>.net11   V  real  (65 points)
        I70.I5<5>.net11   V  real  (65 points)
        I70.I5<6>.net11   V  real  (65 points)
        I70.I5<7>.net11   V  real  (65 points)
        I70.I5<8>.net11   V  real  (65 points)
        I70.I5<9>.net11   V  real  (65 points)
        I70.I6<0>.net11   V  real  (65 points)
        I70.I6<10>.net11  V  real  (65 points)
        I70.I6<11>.net11  V  real  (65 points)
        I70.I6<1>.net11   V  real  (65 points)
        I70.I6<2>.net11   V  real  (65 points)
        I70.I6<3>.net11   V  real  (65 points)
        I70.I6<4>.net11   V  real  (65 points)
        I70.I6<5>.net11   V  real  (65 points)
        I70.I6<6>.net11   V  real  (65 points)
        I70.I6<7>.net11   V  real  (65 points)
        I70.I6<8>.net11   V  real  (65 points)
        I70.I6<9>.net11   V  real  (65 points)
        I70.I7<0>.net11   V  real  (65 points)
        I70.I7<10>.net11  V  real  (65 points)
        I70.I7<11>.net11  V  real  (65 points)
        I70.I7<1>.net11   V  real  (65 points)
        I70.I7<2>.net11   V  real  (65 points)
        I70.I7<3>.net11   V  real  (65 points)
        I70.I7<4>.net11   V  real  (65 points)
        I70.I7<5>.net11   V  real  (65 points)
        I70.I7<6>.net11   V  real  (65 points)
        I70.I7<7>.net11   V  real  (65 points)
        I70.I7<8>.net11   V  real  (65 points)
        I70.I7<9>.net11   V  real  (65 points)
        I70.net1<0>       V  real  (65 points)
        I70.net1<10>      V  real  (65 points)
        I70.net1<11>      V  real  (65 points)
        I70.net1<1>       V  real  (65 points)
        I70.net1<2>       V  real  (65 points)
        I70.net1<3>       V  real  (65 points)
        I70.net1<4>       V  real  (65 points)
        I70.net1<5>       V  real  (65 points)
        I70.net1<6>       V  real  (65 points)
        I70.net1<7>       V  real  (65 points)
        I70.net1<8>       V  real  (65 points)
        I70.net1<9>       V  real  (65 points)
        I70.net2<0>       V  real  (65 points)
        I70.net2<10>      V  real  (65 points)
        I70.net2<11>      V  real  (65 points)
        I70.net2<1>       V  real  (65 points)
        I70.net2<2>       V  real  (65 points)
        I70.net2<3>       V  real  (65 points)
        I70.net2<4>       V  real  (65 points)
        I70.net2<5>       V  real  (65 points)
        I70.net2<6>       V  real  (65 points)
        I70.net2<7>       V  real  (65 points)
        I70.net2<8>       V  real  (65 points)
        I70.net2<9>       V  real  (65 points)
        I70.net3<0>       V  real  (65 points)
        I70.net3<10>      V  real  (65 points)
        I70.net3<11>      V  real  (65 points)
        I70.net3<1>       V  real  (65 points)
        I70.net3<2>       V  real  (65 points)
        I70.net3<3>       V  real  (65 points)
        I70.net3<4>       V  real  (65 points)
        I70.net3<5>       V  real  (65 points)
        I70.net3<6>       V  real  (65 points)
        I70.net3<7>       V  real  (65 points)
        I70.net3<8>       V  real  (65 points)
        I70.net3<9>       V  real  (65 points)
        I71.I1.net9       V  real  (65 points)
        I71.I10.net9      V  real  (65 points)
        I71.I11.net9      V  real  (65 points)
        I71.I12.net9      V  real  (65 points)
        I71.I13.net9      V  real  (65 points)
        I71.I14.net9      V  real  (65 points)
        I71.I15.net9      V  real  (65 points)
        I71.I16.net9      V  real  (65 points)
        I71.I17.net9      V  real  (65 points)
        I71.I2.net9       V  real  (65 points)
        I71.I3.net9       V  real  (65 points)
        I71.I30.net9      V  real  (65 points)
        I71.I31.net9      V  real  (65 points)
        I71.I32.net9      V  real  (65 points)
        I71.I33.net9      V  real  (65 points)
        I71.I4.net9       V  real  (65 points)
        I71.I5.net9       V  real  (65 points)
        I71.I6.net9       V  real  (65 points)
        I71.I7.net9       V  real  (65 points)
        I71.I8.net9       V  real  (65 points)
        I71.I9.net9       V  real  (65 points)
        I71.net1          V  real  (65 points)
        I71.net15         V  real  (65 points)
        I71.net16         V  real  (65 points)
        I71.net17         V  real  (65 points)
        I71.net18         V  real  (65 points)
        I71.net19         V  real  (65 points)
        I71.net2          V  real  (65 points)
        I71.net20         V  real  (65 points)
        I71.net21         V  real  (65 points)
        I71.net22         V  real  (65 points)
        I72.I0.net9       V  real  (65 points)
        I72.I1.net9       V  real  (65 points)
        I72.I10.net9      V  real  (65 points)
        I72.I11.net9      V  real  (65 points)
        I72.I12.net9      V  real  (65 points)
        I72.I13.net9      V  real  (65 points)
        I72.I14.net9      V  real  (65 points)
        I72.I15.net9      V  real  (65 points)
        I72.I16.net9      V  real  (65 points)
        I72.I17.net9      V  real  (65 points)
        I72.I2.net9       V  real  (65 points)
        I72.I3.net9       V  real  (65 points)
        I72.I30.net9      V  real  (65 points)
        I72.I31.net9      V  real  (65 points)
        I72.I32.net9      V  real  (65 points)
        I72.I33.net9      V  real  (65 points)
        I72.I4.net9       V  real  (65 points)
        I72.I5.net9       V  real  (65 points)
        I72.I6.net9       V  real  (65 points)
        I72.I7.net9       V  real  (65 points)
        I72.I8.net9       V  real  (65 points)
        I72.I9.net9       V  real  (65 points)
        I72.net1          V  real  (65 points)
        I72.net15         V  real  (65 points)
        I72.net16         V  real  (65 points)
        I72.net17         V  real  (65 points)
        I72.net18         V  real  (65 points)
        I72.net19         V  real  (65 points)
        I72.net2          V  real  (65 points)
        I72.net20         V  real  (65 points)
        I72.net21         V  real  (65 points)
        I72.net22         V  real  (65 points)
        I72.net23         V  real  (65 points)
        I73.I1.net9       V  real  (65 points)
        I73.I10.net9      V  real  (65 points)
        I73.I11.net9      V  real  (65 points)
        I73.I12.net9      V  real  (65 points)
        I73.I13.net9      V  real  (65 points)
        I73.I14.net9      V  real  (65 points)
        I73.I15.net9      V  real  (65 points)
        I73.I16.net9      V  real  (65 points)
        I73.I17.net9      V  real  (65 points)
        I73.I2.net9       V  real  (65 points)
        I73.I3.net9       V  real  (65 points)
        I73.I30.net9      V  real  (65 points)
        I73.I31.net9      V  real  (65 points)
        I73.I32.net9      V  real  (65 points)
        I73.I33.net9      V  real  (65 points)
        I73.I4.net9       V  real  (65 points)
        I73.I5.net9       V  real  (65 points)
        I73.I6.net9       V  real  (65 points)
        I73.I7.net9       V  real  (65 points)
        I73.I8.net9       V  real  (65 points)
        I73.I9.net9       V  real  (65 points)
        I73.net1          V  real  (65 points)
        I73.net15         V  real  (65 points)
        I73.net16         V  real  (65 points)
        I73.net17         V  real  (65 points)
        I73.net18         V  real  (65 points)
        I73.net19         V  real  (65 points)
        I73.net2          V  real  (65 points)
        I73.net20         V  real  (65 points)
        I73.net21         V  real  (65 points)
        I73.net22         V  real  (65 points)
        V0:p              A  real  (65 points)
        V1:p              A  real  (65 points)
        V2:p              A  real  (65 points)
        V3:p              A  real  (65 points)
        V6:p              A  real  (65 points)
        V7:p              A  real  (65 points)
        conM<0>           V  real  (65 points)
        conM<10>          V  real  (65 points)
        conM<11>          V  real  (65 points)
        conM<1>           V  real  (65 points)
        conM<2>           V  real  (65 points)
        conM<3>           V  real  (65 points)
        conM<4>           V  real  (65 points)
        conM<5>           V  real  (65 points)
        conM<6>           V  real  (65 points)
        conM<7>           V  real  (65 points)
        conM<8>           V  real  (65 points)
        conM<9>           V  real  (65 points)
        conP<0>           V  real  (65 points)
        conP<10>          V  real  (65 points)
        conP<11>          V  real  (65 points)
        conP<1>           V  real  (65 points)
        conP<2>           V  real  (65 points)
        conP<3>           V  real  (65 points)
        conP<4>           V  real  (65 points)
        conP<5>           V  real  (65 points)
        conP<6>           V  real  (65 points)
        conP<7>           V  real  (65 points)
        conP<8>           V  real  (65 points)
        conP<9>           V  real  (65 points)
        net1<0>           V  real  (65 points)
        net1<10>          V  real  (65 points)
        net1<1>           V  real  (65 points)
        net1<2>           V  real  (65 points)
        net1<3>           V  real  (65 points)
        net1<4>           V  real  (65 points)
        net1<5>           V  real  (65 points)
        net1<6>           V  real  (65 points)
        net1<7>           V  real  (65 points)
        net1<8>           V  real  (65 points)
        net1<9>           V  real  (65 points)
        net2<0>           V  real  (65 points)
        net2<10>          V  real  (65 points)
        net2<1>           V  real  (65 points)
        net2<2>           V  real  (65 points)
        net2<3>           V  real  (65 points)
        net2<4>           V  real  (65 points)
        net2<5>           V  real  (65 points)
        net2<6>           V  real  (65 points)
        net2<7>           V  real  (65 points)
        net2<8>           V  real  (65 points)
        net2<9>           V  real  (65 points)
        net4<0>           V  real  (65 points)
        net4<10>          V  real  (65 points)
        net4<1>           V  real  (65 points)
        net4<2>           V  real  (65 points)
        net4<3>           V  real  (65 points)
        net4<4>           V  real  (65 points)
        net4<5>           V  real  (65 points)
        net4<6>           V  real  (65 points)
        net4<7>           V  real  (65 points)
        net4<8>           V  real  (65 points)
        net4<9>           V  real  (65 points)
        net7<0>           V  real  (65 points)
        net7<10>          V  real  (65 points)
        net7<1>           V  real  (65 points)
        net7<2>           V  real  (65 points)
        net7<3>           V  real  (65 points)
        net7<4>           V  real  (65 points)
        net7<5>           V  real  (65 points)
        net7<6>           V  real  (65 points)
        net7<7>           V  real  (65 points)
        net7<8>           V  real  (65 points)
        net7<9>           V  real  (65 points)
        phiC              V  real  (65 points)
        phiS              V  real  (65 points)
        phi_ext           V  real  (65 points)
        vdd               V  real  (65 points)
        vic               V  real  (65 points)
        vid               V  real  (65 points)
        vim               V  real  (65 points)
        vimth             V  real  (65 points)
        vip               V  real  (65 points)
        vipth             V  real  (65 points)
        vod               V  real  (65 points)
        voutm             V  real  (65 points)
        voutp             V  real  (65 points)
        vref              V  real  (65 points)
        vss               V  real  (65 points)
    """.strip()
    for line in signals.splitlines():
        components = line.split()
        if len(components) == 5:
            name, units, kind, _, _ = components
        else:
            name, kind, _, _ = components
            units = ''
        type_maps = dict(
            real = ['float double'],
            complex = ['complex double'],
            integer = ['int byte', 'int long', 'int'],
        )
        signal = psf.get_signal(name)
        assert name == signal.name, signal.name
        assert units == PSF.units_to_unicode(signal.units), signal.name
        assert signal.type.kind in type_maps[kind], signal.name


def test_asereq():
    # ignore backslashes in names
    psf = PSF('samples/asereq.dcop')
    signals = """
        C1.cap                   F      real
        C2.cap                   F      real
        I1.i                     A      real
        I1.pwr                   W      real
        I1.v                     V      real
        I10.i                    A      real
        I10.pwr                  W      real
        I10.v                    V      real
        I2.i                     A      real
        I2.pwr                   W      real
        I2.v                     V      real
        M1.cfrolgd.cap           F      real
        M1.cfrolgs.cap           F      real
        M1.cfrowgd.cap           F      real
        M1.cfrowgs.cap           F      real
        M1.cgn.cap               F      real
        M1.csdext.cap            F      real
        M1.m1.beff                      real
        M1.m1.cbb                C      real
        M1.m1.cbd                C      real
        M1.m1.cbg                C      real
        M1.m1.cbs                C      real
        M1.m1.cdb                C      real
        M1.m1.cdd                C      real
        M1.m1.cdg                C      real
        M1.m1.cds                C      real
        M1.m1.cgb                C      real
        M1.m1.cgd                C      real
        M1.m1.cgg                C      real
        M1.m1.cgs                C      real
        M1.m1.csb                C      real
        M1.m1.csd                C      real
        M1.m1.csg                C      real
        M1.m1.css                C      real
        M1.m1.dtsh                      real
        M1.m1.ft                        real
        M1.m1.gds                       real
        M1.m1.gm                        real
        M1.m1.gmb                       real
        M1.m1.gmoverid                  real
        M1.m1.ib                 I      real
        M1.m1.id                 I      real
        M1.m1.idb                I      real
        M1.m1.ids                I      real
        M1.m1.ig                 I      real
        M1.m1.igd                I      real
        M1.m1.igidl              I      real
        M1.m1.igisl              I      real
        M1.m1.igs                I      real
        M1.m1.is                 I      real
        M1.m1.isb                I      real
        M1.m1.pwr                W      real
        M1.m1.region                    integer
        M1.m1.rgate              R      real
        M1.m1.rout               R      real
        M1.m1.self_gain                 real
        M1.m1.tk                        real
        M1.m1.typeop                    real
        M1.m1.vds                V      real
        M1.m1.vdsat              V      real
        M1.m1.vdsat_marg         V      real
        M1.m1.vearly             V      real
        M1.m1.vgs                V      real
        M1.m1.vsb                V      real
        M1.m1.vth                V      real
        M1.m1.vth_drive          V      real
        M1.rb.i                  A      real
        M1.rb.pwr                W      real
        M1.rb.res                Ω      real
        M1.rb.v                  V      real
        M1.rgcs.i                A      real
        M1.rgcs.pwr              W      real
        M1.rgcs.res              Ω      real
        M1.rgcs.v                V      real
        M1.rgn.i                 A      real
        M1.rgn.pwr               W      real
        M1.rgn.res               Ω      real
        M1.rgn.v                 V      real
        M1.rgvi.i                A      real
        M1.rgvi.pwr              W      real
        M1.rgvi.res              Ω      real
        M1.rgvi.v                V      real
        M1.xdw.d1.cj             F      real
        M1.xdw.d1.cjbot          F      real
        M1.xdw.d1.cjgat          F      real
        M1.xdw.d1.cjosbot        F      real
        M1.xdw.d1.cjosgat        F      real
        M1.xdw.d1.cjossti        F      real
        M1.xdw.d1.cjsti          F      real
        M1.xdw.d1.ctotal         F      real
        M1.xdw.d1.diode_region          integer
        M1.xdw.d1.idsatsbot      A      real
        M1.xdw.d1.idsatsgat      A      real
        M1.xdw.d1.idsatssti      A      real
        M1.xdw.d1.ij             A      real
        M1.xdw.d1.ijbot          A      real
        M1.xdw.d1.ijgat          A      real
        M1.xdw.d1.ijsti          A      real
        M1.xdw.d1.lx5            F      real
        M1.xdw.d1.si             A²/Hz  real
        M1.xdw.d1.vak            V      real
        M1.xdw.d1.vbisbot        V      real
        M1.xdw.d1.vbisgat        V      real
        M1.xdw.d1.vbissti        V      real
        M1.xdw:1.i               A      real
        M1.xdw:2.i               A      real
        M11.cfrolgd.cap          F      real
        M11.cfrolgs.cap          F      real
        M11.cfrowgd.cap          F      real
        M11.cfrowgs.cap          F      real
        M11.cgn.cap              F      real
        M11.csdext.cap           F      real
        M11.m1.beff                     real
        M11.m1.cbb               C      real
        M11.m1.cbd               C      real
        M11.m1.cbg               C      real
        M11.m1.cbs               C      real
        M11.m1.cdb               C      real
        M11.m1.cdd               C      real
        M11.m1.cdg               C      real
        M11.m1.cds               C      real
        M11.m1.cgb               C      real
        M11.m1.cgd               C      real
        M11.m1.cgg               C      real
        M11.m1.cgs               C      real
        M11.m1.csb               C      real
        M11.m1.csd               C      real
        M11.m1.csg               C      real
        M11.m1.css               C      real
        M11.m1.dtsh                     real
        M11.m1.ft                       real
        M11.m1.gds                      real
        M11.m1.gm                       real
        M11.m1.gmb                      real
        M11.m1.gmoverid                 real
        M11.m1.ib                I      real
        M11.m1.id                I      real
        M11.m1.idb               I      real
        M11.m1.ids               I      real
        M11.m1.ig                I      real
        M11.m1.igd               I      real
        M11.m1.igidl             I      real
        M11.m1.igisl             I      real
        M11.m1.igs               I      real
        M11.m1.is                I      real
        M11.m1.isb               I      real
        M11.m1.pwr               W      real
        M11.m1.region                   integer
        M11.m1.rgate             R      real
        M11.m1.rout              R      real
        M11.m1.self_gain                real
        M11.m1.tk                       real
        M11.m1.typeop                   real
        M11.m1.vds               V      real
        M11.m1.vdsat             V      real
        M11.m1.vdsat_marg        V      real
        M11.m1.vearly            V      real
        M11.m1.vgs               V      real
        M11.m1.vsb               V      real
        M11.m1.vth               V      real
        M11.m1.vth_drive         V      real
        M11.rb.i                 A      real
        M11.rb.pwr               W      real
        M11.rb.res               Ω      real
        M11.rb.v                 V      real
        M11.rgcs.i               A      real
        M11.rgcs.pwr             W      real
        M11.rgcs.res             Ω      real
        M11.rgcs.v               V      real
        M11.rgn.i                A      real
        M11.rgn.pwr              W      real
        M11.rgn.res              Ω      real
        M11.rgn.v                V      real
        M11.rgvi.i               A      real
        M11.rgvi.pwr             W      real
        M11.rgvi.res             Ω      real
        M11.rgvi.v               V      real
        M11.xdw.d1.cj            F      real
        M11.xdw.d1.cjbot         F      real
        M11.xdw.d1.cjgat         F      real
        M11.xdw.d1.cjosbot       F      real
        M11.xdw.d1.cjosgat       F      real
        M11.xdw.d1.cjossti       F      real
        M11.xdw.d1.cjsti         F      real
        M11.xdw.d1.ctotal        F      real
        M11.xdw.d1.diode_region         integer
        M11.xdw.d1.idsatsbot     A      real
        M11.xdw.d1.idsatsgat     A      real
        M11.xdw.d1.idsatssti     A      real
        M11.xdw.d1.ij            A      real
        M11.xdw.d1.ijbot         A      real
        M11.xdw.d1.ijgat         A      real
        M11.xdw.d1.ijsti         A      real
        M11.xdw.d1.lx5           F      real
        M11.xdw.d1.si            A²/Hz  real
        M11.xdw.d1.vak           V      real
        M11.xdw.d1.vbisbot       V      real
        M11.xdw.d1.vbisgat       V      real
        M11.xdw.d1.vbissti       V      real
        M11.xdw:1.i              A      real
        M11.xdw:2.i              A      real
        M11:1.i                  A      real
        M11:2.i                  A      real
        M11:3.i                  A      real
        M11:4.i                  A      real
        M12.cfrolgd.cap          F      real
        M12.cfrolgs.cap          F      real
        M12.cfrowgd.cap          F      real
        M12.cfrowgs.cap          F      real
        M12.cgn.cap              F      real
        M12.csdext.cap           F      real
        M12.m1.beff                     real
        M12.m1.cbb               C      real
        M12.m1.cbd               C      real
        M12.m1.cbg               C      real
        M12.m1.cbs               C      real
        M12.m1.cdb               C      real
        M12.m1.cdd               C      real
        M12.m1.cdg               C      real
        M12.m1.cds               C      real
        M12.m1.cgb               C      real
        M12.m1.cgd               C      real
        M12.m1.cgg               C      real
        M12.m1.cgs               C      real
        M12.m1.csb               C      real
        M12.m1.csd               C      real
        M12.m1.csg               C      real
        M12.m1.css               C      real
        M12.m1.dtsh                     real
        M12.m1.ft                       real
        M12.m1.gds                      real
        M12.m1.gm                       real
        M12.m1.gmb                      real
        M12.m1.gmoverid                 real
        M12.m1.ib                I      real
        M12.m1.id                I      real
        M12.m1.idb               I      real
        M12.m1.ids               I      real
        M12.m1.ig                I      real
        M12.m1.igd               I      real
        M12.m1.igidl             I      real
        M12.m1.igisl             I      real
        M12.m1.igs               I      real
        M12.m1.is                I      real
        M12.m1.isb               I      real
        M12.m1.pwr               W      real
        M12.m1.region                   integer
        M12.m1.rgate             R      real
        M12.m1.rout              R      real
        M12.m1.self_gain                real
        M12.m1.tk                       real
        M12.m1.typeop                   real
        M12.m1.vds               V      real
        M12.m1.vdsat             V      real
        M12.m1.vdsat_marg        V      real
        M12.m1.vearly            V      real
        M12.m1.vgs               V      real
        M12.m1.vsb               V      real
        M12.m1.vth               V      real
        M12.m1.vth_drive         V      real
        M12.rb.i                 A      real
        M12.rb.pwr               W      real
        M12.rb.res               Ω      real
        M12.rb.v                 V      real
        M12.rgcs.i               A      real
        M12.rgcs.pwr             W      real
        M12.rgcs.res             Ω      real
        M12.rgcs.v               V      real
        M12.rgn.i                A      real
        M12.rgn.pwr              W      real
        M12.rgn.res              Ω      real
        M12.rgn.v                V      real
        M12.rgvi.i               A      real
        M12.rgvi.pwr             W      real
        M12.rgvi.res             Ω      real
        M12.rgvi.v               V      real
        M12.xdw.d1.cj            F      real
        M12.xdw.d1.cjbot         F      real
        M12.xdw.d1.cjgat         F      real
        M12.xdw.d1.cjosbot       F      real
        M12.xdw.d1.cjosgat       F      real
        M12.xdw.d1.cjossti       F      real
        M12.xdw.d1.cjsti         F      real
        M12.xdw.d1.ctotal        F      real
        M12.xdw.d1.diode_region         integer
        M12.xdw.d1.idsatsbot     A      real
        M12.xdw.d1.idsatsgat     A      real
        M12.xdw.d1.idsatssti     A      real
        M12.xdw.d1.ij            A      real
        M12.xdw.d1.ijbot         A      real
        M12.xdw.d1.ijgat         A      real
        M12.xdw.d1.ijsti         A      real
        M12.xdw.d1.lx5           F      real
        M12.xdw.d1.si            A²/Hz  real
        M12.xdw.d1.vak           V      real
        M12.xdw.d1.vbisbot       V      real
        M12.xdw.d1.vbisgat       V      real
        M12.xdw.d1.vbissti       V      real
        M12.xdw:1.i              A      real
        M12.xdw:2.i              A      real
        M12:1.i                  A      real
        M12:2.i                  A      real
        M12:3.i                  A      real
        M12:4.i                  A      real
        M1:1.i                   A      real
        M1:2.i                   A      real
        M1:3.i                   A      real
        M1:4.i                   A      real
        M2.cfrolgd.cap           F      real
        M2.cfrolgs.cap           F      real
        M2.cfrowgd.cap           F      real
        M2.cfrowgs.cap           F      real
        M2.cgn.cap               F      real
        M2.csdext.cap            F      real
        M2.m1.beff                      real
        M2.m1.cbb                C      real
        M2.m1.cbd                C      real
        M2.m1.cbg                C      real
        M2.m1.cbs                C      real
        M2.m1.cdb                C      real
        M2.m1.cdd                C      real
        M2.m1.cdg                C      real
        M2.m1.cds                C      real
        M2.m1.cgb                C      real
        M2.m1.cgd                C      real
        M2.m1.cgg                C      real
        M2.m1.cgs                C      real
        M2.m1.csb                C      real
        M2.m1.csd                C      real
        M2.m1.csg                C      real
        M2.m1.css                C      real
        M2.m1.dtsh                      real
        M2.m1.ft                        real
        M2.m1.gds                       real
        M2.m1.gm                        real
        M2.m1.gmb                       real
        M2.m1.gmoverid                  real
        M2.m1.ib                 I      real
        M2.m1.id                 I      real
        M2.m1.idb                I      real
        M2.m1.ids                I      real
        M2.m1.ig                 I      real
        M2.m1.igd                I      real
        M2.m1.igidl              I      real
        M2.m1.igisl              I      real
        M2.m1.igs                I      real
        M2.m1.is                 I      real
        M2.m1.isb                I      real
        M2.m1.pwr                W      real
        M2.m1.region                    integer
        M2.m1.rgate              R      real
        M2.m1.rout               R      real
        M2.m1.self_gain                 real
        M2.m1.tk                        real
        M2.m1.typeop                    real
        M2.m1.vds                V      real
        M2.m1.vdsat              V      real
        M2.m1.vdsat_marg         V      real
        M2.m1.vearly             V      real
        M2.m1.vgs                V      real
        M2.m1.vsb                V      real
        M2.m1.vth                V      real
        M2.m1.vth_drive          V      real
        M2.rb.i                  A      real
        M2.rb.pwr                W      real
        M2.rb.res                Ω      real
        M2.rb.v                  V      real
        M2.rgcs.i                A      real
        M2.rgcs.pwr              W      real
        M2.rgcs.res              Ω      real
        M2.rgcs.v                V      real
        M2.rgn.i                 A      real
        M2.rgn.pwr               W      real
        M2.rgn.res               Ω      real
        M2.rgn.v                 V      real
        M2.rgvi.i                A      real
        M2.rgvi.pwr              W      real
        M2.rgvi.res              Ω      real
        M2.rgvi.v                V      real
        M2.xdw.d1.cj             F      real
        M2.xdw.d1.cjbot          F      real
        M2.xdw.d1.cjgat          F      real
        M2.xdw.d1.cjosbot        F      real
        M2.xdw.d1.cjosgat        F      real
        M2.xdw.d1.cjossti        F      real
        M2.xdw.d1.cjsti          F      real
        M2.xdw.d1.ctotal         F      real
        M2.xdw.d1.diode_region          integer
        M2.xdw.d1.idsatsbot      A      real
        M2.xdw.d1.idsatsgat      A      real
        M2.xdw.d1.idsatssti      A      real
        M2.xdw.d1.ij             A      real
        M2.xdw.d1.ijbot          A      real
        M2.xdw.d1.ijgat          A      real
        M2.xdw.d1.ijsti          A      real
        M2.xdw.d1.lx5            F      real
        M2.xdw.d1.si             A²/Hz  real
        M2.xdw.d1.vak            V      real
        M2.xdw.d1.vbisbot        V      real
        M2.xdw.d1.vbisgat        V      real
        M2.xdw.d1.vbissti        V      real
        M2.xdw:1.i               A      real
        M2.xdw:2.i               A      real
        M21.cfrolgd.cap          F      real
        M21.cfrolgs.cap          F      real
        M21.cfrowgd.cap          F      real
        M21.cfrowgs.cap          F      real
        M21.cgn.cap              F      real
        M21.csdext.cap           F      real
        M21.m1.beff                     real
        M21.m1.cbb               C      real
        M21.m1.cbd               C      real
        M21.m1.cbg               C      real
        M21.m1.cbs               C      real
        M21.m1.cdb               C      real
        M21.m1.cdd               C      real
        M21.m1.cdg               C      real
        M21.m1.cds               C      real
        M21.m1.cgb               C      real
        M21.m1.cgd               C      real
        M21.m1.cgg               C      real
        M21.m1.cgs               C      real
        M21.m1.csb               C      real
        M21.m1.csd               C      real
        M21.m1.csg               C      real
        M21.m1.css               C      real
        M21.m1.dtsh                     real
        M21.m1.ft                       real
        M21.m1.gds                      real
        M21.m1.gm                       real
        M21.m1.gmb                      real
        M21.m1.gmoverid                 real
        M21.m1.ib                I      real
        M21.m1.id                I      real
        M21.m1.idb               I      real
        M21.m1.ids               I      real
        M21.m1.ig                I      real
        M21.m1.igd               I      real
        M21.m1.igidl             I      real
        M21.m1.igisl             I      real
        M21.m1.igs               I      real
        M21.m1.is                I      real
        M21.m1.isb               I      real
        M21.m1.pwr               W      real
        M21.m1.region                   integer
        M21.m1.rgate             R      real
        M21.m1.rout              R      real
        M21.m1.self_gain                real
        M21.m1.tk                       real
        M21.m1.typeop                   real
        M21.m1.vds               V      real
        M21.m1.vdsat             V      real
        M21.m1.vdsat_marg        V      real
        M21.m1.vearly            V      real
        M21.m1.vgs               V      real
        M21.m1.vsb               V      real
        M21.m1.vth               V      real
        M21.m1.vth_drive         V      real
        M21.rb.i                 A      real
        M21.rb.pwr               W      real
        M21.rb.res               Ω      real
        M21.rb.v                 V      real
        M21.rgcs.i               A      real
        M21.rgcs.pwr             W      real
        M21.rgcs.res             Ω      real
        M21.rgcs.v               V      real
        M21.rgn.i                A      real
        M21.rgn.pwr              W      real
        M21.rgn.res              Ω      real
        M21.rgn.v                V      real
        M21.rgvi.i               A      real
        M21.rgvi.pwr             W      real
        M21.rgvi.res             Ω      real
        M21.rgvi.v               V      real
        M21.xdw.d1.cj            F      real
        M21.xdw.d1.cjbot         F      real
        M21.xdw.d1.cjgat         F      real
        M21.xdw.d1.cjosbot       F      real
        M21.xdw.d1.cjosgat       F      real
        M21.xdw.d1.cjossti       F      real
        M21.xdw.d1.cjsti         F      real
        M21.xdw.d1.ctotal        F      real
        M21.xdw.d1.diode_region         integer
        M21.xdw.d1.idsatsbot     A      real
        M21.xdw.d1.idsatsgat     A      real
        M21.xdw.d1.idsatssti     A      real
        M21.xdw.d1.ij            A      real
        M21.xdw.d1.ijbot         A      real
        M21.xdw.d1.ijgat         A      real
        M21.xdw.d1.ijsti         A      real
        M21.xdw.d1.lx5           F      real
        M21.xdw.d1.si            A²/Hz  real
        M21.xdw.d1.vak           V      real
        M21.xdw.d1.vbisbot       V      real
        M21.xdw.d1.vbisgat       V      real
        M21.xdw.d1.vbissti       V      real
        M21.xdw:1.i              A      real
        M21.xdw:2.i              A      real
        M21:1.i                  A      real
        M21:2.i                  A      real
        M21:3.i                  A      real
        M21:4.i                  A      real
        M22.cfrolgd.cap          F      real
        M22.cfrolgs.cap          F      real
        M22.cfrowgd.cap          F      real
        M22.cfrowgs.cap          F      real
        M22.cgn.cap              F      real
        M22.csdext.cap           F      real
        M22.m1.beff                     real
        M22.m1.cbb               C      real
        M22.m1.cbd               C      real
        M22.m1.cbg               C      real
        M22.m1.cbs               C      real
        M22.m1.cdb               C      real
        M22.m1.cdd               C      real
        M22.m1.cdg               C      real
        M22.m1.cds               C      real
        M22.m1.cgb               C      real
        M22.m1.cgd               C      real
        M22.m1.cgg               C      real
        M22.m1.cgs               C      real
        M22.m1.csb               C      real
        M22.m1.csd               C      real
        M22.m1.csg               C      real
        M22.m1.css               C      real
        M22.m1.dtsh                     real
        M22.m1.ft                       real
        M22.m1.gds                      real
        M22.m1.gm                       real
        M22.m1.gmb                      real
        M22.m1.gmoverid                 real
        M22.m1.ib                I      real
        M22.m1.id                I      real
        M22.m1.idb               I      real
        M22.m1.ids               I      real
        M22.m1.ig                I      real
        M22.m1.igd               I      real
        M22.m1.igidl             I      real
        M22.m1.igisl             I      real
        M22.m1.igs               I      real
        M22.m1.is                I      real
        M22.m1.isb               I      real
        M22.m1.pwr               W      real
        M22.m1.region                   integer
        M22.m1.rgate             R      real
        M22.m1.rout              R      real
        M22.m1.self_gain                real
        M22.m1.tk                       real
        M22.m1.typeop                   real
        M22.m1.vds               V      real
        M22.m1.vdsat             V      real
        M22.m1.vdsat_marg        V      real
        M22.m1.vearly            V      real
        M22.m1.vgs               V      real
        M22.m1.vsb               V      real
        M22.m1.vth               V      real
        M22.m1.vth_drive         V      real
        M22.rb.i                 A      real
        M22.rb.pwr               W      real
        M22.rb.res               Ω      real
        M22.rb.v                 V      real
        M22.rgcs.i               A      real
        M22.rgcs.pwr             W      real
        M22.rgcs.res             Ω      real
        M22.rgcs.v               V      real
        M22.rgn.i                A      real
        M22.rgn.pwr              W      real
        M22.rgn.res              Ω      real
        M22.rgn.v                V      real
        M22.rgvi.i               A      real
        M22.rgvi.pwr             W      real
        M22.rgvi.res             Ω      real
        M22.rgvi.v               V      real
        M22.xdw.d1.cj            F      real
        M22.xdw.d1.cjbot         F      real
        M22.xdw.d1.cjgat         F      real
        M22.xdw.d1.cjosbot       F      real
        M22.xdw.d1.cjosgat       F      real
        M22.xdw.d1.cjossti       F      real
        M22.xdw.d1.cjsti         F      real
        M22.xdw.d1.ctotal        F      real
        M22.xdw.d1.diode_region         integer
        M22.xdw.d1.idsatsbot     A      real
        M22.xdw.d1.idsatsgat     A      real
        M22.xdw.d1.idsatssti     A      real
        M22.xdw.d1.ij            A      real
        M22.xdw.d1.ijbot         A      real
        M22.xdw.d1.ijgat         A      real
        M22.xdw.d1.ijsti         A      real
        M22.xdw.d1.lx5           F      real
        M22.xdw.d1.si            A²/Hz  real
        M22.xdw.d1.vak           V      real
        M22.xdw.d1.vbisbot       V      real
        M22.xdw.d1.vbisgat       V      real
        M22.xdw.d1.vbissti       V      real
        M22.xdw:1.i              A      real
        M22.xdw:2.i              A      real
        M22:1.i                  A      real
        M22:2.i                  A      real
        M22:3.i                  A      real
        M22:4.i                  A      real
        M2:1.i                   A      real
        M2:2.i                   A      real
        M2:3.i                   A      real
        M2:4.i                   A      real
        N0.cfrolgd.cap           F      real
        N0.cfrolgs.cap           F      real
        N0.cfrowgd.cap           F      real
        N0.cfrowgs.cap           F      real
        N0.cgn.cap               F      real
        N0.csdext.cap            F      real
        N0.m1.beff                      real
        N0.m1.cbb                C      real
        N0.m1.cbd                C      real
        N0.m1.cbg                C      real
        N0.m1.cbs                C      real
        N0.m1.cdb                C      real
        N0.m1.cdd                C      real
        N0.m1.cdg                C      real
        N0.m1.cds                C      real
        N0.m1.cgb                C      real
        N0.m1.cgd                C      real
        N0.m1.cgg                C      real
        N0.m1.cgs                C      real
        N0.m1.csb                C      real
        N0.m1.csd                C      real
        N0.m1.csg                C      real
        N0.m1.css                C      real
        N0.m1.dtsh                      real
        N0.m1.ft                        real
        N0.m1.gds                       real
        N0.m1.gm                        real
        N0.m1.gmb                       real
        N0.m1.gmoverid                  real
        N0.m1.ib                 I      real
        N0.m1.id                 I      real
        N0.m1.idb                I      real
        N0.m1.ids                I      real
        N0.m1.ig                 I      real
        N0.m1.igd                I      real
        N0.m1.igidl              I      real
        N0.m1.igisl              I      real
        N0.m1.igs                I      real
        N0.m1.is                 I      real
        N0.m1.isb                I      real
        N0.m1.pwr                W      real
        N0.m1.region                    integer
        N0.m1.rgate              R      real
        N0.m1.rout               R      real
        N0.m1.self_gain                 real
        N0.m1.tk                        real
        N0.m1.typeop                    real
        N0.m1.vds                V      real
        N0.m1.vdsat              V      real
        N0.m1.vdsat_marg         V      real
        N0.m1.vearly             V      real
        N0.m1.vgs                V      real
        N0.m1.vsb                V      real
        N0.m1.vth                V      real
        N0.m1.vth_drive          V      real
        N0.rb.i                  A      real
        N0.rb.pwr                W      real
        N0.rb.res                Ω      real
        N0.rb.v                  V      real
        N0.rgcs.i                A      real
        N0.rgcs.pwr              W      real
        N0.rgcs.res              Ω      real
        N0.rgcs.v                V      real
        N0.rgn.i                 A      real
        N0.rgn.pwr               W      real
        N0.rgn.res               Ω      real
        N0.rgn.v                 V      real
        N0.rgvi.i                A      real
        N0.rgvi.pwr              W      real
        N0.rgvi.res              Ω      real
        N0.rgvi.v                V      real
        N0.xdw.d1.cj             F      real
        N0.xdw.d1.cjbot          F      real
        N0.xdw.d1.cjgat          F      real
        N0.xdw.d1.cjosbot        F      real
        N0.xdw.d1.cjosgat        F      real
        N0.xdw.d1.cjossti        F      real
        N0.xdw.d1.cjsti          F      real
        N0.xdw.d1.ctotal         F      real
        N0.xdw.d1.diode_region          integer
        N0.xdw.d1.idsatsbot      A      real
        N0.xdw.d1.idsatsgat      A      real
        N0.xdw.d1.idsatssti      A      real
        N0.xdw.d1.ij             A      real
        N0.xdw.d1.ijbot          A      real
        N0.xdw.d1.ijgat          A      real
        N0.xdw.d1.ijsti          A      real
        N0.xdw.d1.lx5            F      real
        N0.xdw.d1.si             A²/Hz  real
        N0.xdw.d1.vak            V      real
        N0.xdw.d1.vbisbot        V      real
        N0.xdw.d1.vbisgat        V      real
        N0.xdw.d1.vbissti        V      real
        N0.xdw:1.i               A      real
        N0.xdw:2.i               A      real
        N0:1.i                   A      real
        N0:2.i                   A      real
        N0:3.i                   A      real
        N0:4.i                   A      real
        V0.i                     A      real
        V0.pwr                   W      real
        V0.v                     V      real
        V1.i                     A      real
        V1.pwr                   W      real
        V1.v                     V      real
        V2.i                     A      real
        V2.pwr                   W      real
        V2.v                     V      real
        V4.i                     A      real
        V4.pwr                   W      real
        V4.v                     V      real
    """.strip()
    for line in signals.splitlines():
        components = line.split()
        if len(components) == 3:
            name, units, kind = components
        else:
            name, kind = components
            units = ''
        type_maps = dict(
            real = ['float double'],
            complex = ['complex double'],
            integer = ['int byte', 'int long', 'int'],
        )
        signal = psf.get_signal(name)
        assert name == signal.name, signal.name
        assert units == PSF.units_to_unicode(signal.units), signal.name
        assert signal.type.kind in type_maps[kind], signal.name


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
