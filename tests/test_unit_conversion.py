# encoding: utf8

from quantiphy import (
    Quantity, UnitConversion,
    QuantiPhyError, IncompatibleUnits, UnknownPreference, UnknownConversion,
    UnknownUnitSystem, InvalidRecognizer, UnknownFormatKey, UnknownScaleFactor,
    InvalidNumber, ExpectedQuantity, MissingName,
)
Quantity.reset_prefs()
import math
import pytest

def test_simple_scaling():
    Quantity.reset_prefs()
    with Quantity.prefs(
        spacer=None, show_label=None, label_fmt=None, label_fmt_full=None
    ):
        q=Quantity('1kg', scale=2)
        qs=Quantity('2ms')
        assert q.render() == '2 kg'
        assert qs.render() == '2 ms'
        assert q.render(scale=0.001) == '2 g'
        assert str(q.scale(0.001)) == '2 g'
        assert q.render(scale=qs) == '4 g'
        assert str(q.scale(qs)) == '4 g'
        with pytest.raises(KeyError) as exception:
            q.render(scale='fuzz')
        assert str(exception.value) == "unable to convert between 'fuzz' and 'g'."
        assert isinstance(exception.value, UnknownConversion)
        assert isinstance(exception.value, QuantiPhyError)
        assert isinstance(exception.value, KeyError)
        assert exception.value.args == ('fuzz', 'g')
        with pytest.raises(KeyError) as exception:
            q.scale('fuzz')
        assert str(exception.value) == "unable to convert between 'fuzz' and 'g'."
        assert isinstance(exception.value, UnknownConversion)
        assert isinstance(exception.value, QuantiPhyError)
        assert isinstance(exception.value, KeyError)
        assert exception.value.args == ('fuzz', 'g')

        q=Quantity('1', units='g', scale=1000)
        assert q.render() == '1 kg'
        assert q.render(scale=(0.0022046, 'lbs')) == '2.2046 lbs'
        assert str(q.scale((0.0022046, 'lbs'))) == '2.2046 lbs'

        q=Quantity('1', units='g', scale=qs)
        assert q.render() == '2 mg'

        q=Quantity('1', scale=(1000, 'g'))
        assert q.render() == '1 kg'
        assert q.render(scale=lambda v, u: (0.0022046*v, 'lbs')) == '2.2046 lbs'

        def dB(v, u):
            assert isinstance(v, Quantity)
            assert v.units == u
            return 20*math.log(v, 10), 'dB'+u

        def adB(v, u):
            assert isinstance(v, Quantity)
            assert v.units == u
            return pow(10, v/20), u[2:] if u.startswith('dB') else u

        q=Quantity('-40 dBV', scale=adB)
        assert q.render() == '10 mV'
        assert q.render(scale=dB) == '-40 dBV'
        assert str(q.scale(dB)) == '-40 dBV'

def test_temperature():
    Quantity.reset_prefs()
    with Quantity.prefs(
        spacer=None, show_label=None, label_fmt=None, label_fmt_full=None,
        ignore_sf=True
    ):
        q=Quantity('100 °C')
        assert q.render() == '100 °C'
        assert q.render(scale='C') == '100 C'
        assert q.render(scale='°C') == '100 °C'
        assert q.render(scale='K') == '373.15 K'
        assert q.render(scale='°F') == '212 °F'
        assert q.render(scale='F') == '212 F'
        assert q.render(scale='°R') == '671.67 °R'
        assert q.render(scale='R') == '671.67 R'

        q=Quantity('100 C')
        assert q.render() == '100 C'
        assert q.render(scale='C') == '100 C'
        assert q.render(scale='K') == '373.15 K'
        assert q.render(scale='F') == '212 F'
        assert q.render(scale='R') == '671.67 R'
        assert q.render(scale='°C') == '100 °C'
        assert q.render(scale='°F') == '212 °F'
        assert q.render(scale='°R') == '671.67 °R'

        q=Quantity('373.15 K')
        assert q.render() == '373.15 K'
        assert q.render(scale='C') == '100 C'
        assert q.render(scale='K') == '373.15 K'
        assert q.render(scale='F') == '212 F'
        assert q.render(scale='R') == '671.67 R'
        assert q.render(scale='°C') == '100 °C'
        assert q.render(scale='°F') == '212 °F'
        assert q.render(scale='°R') == '671.67 °R'

        q=Quantity('212 °F')
        assert q.render() == '212 °F'
        assert q.render(scale='°C') == '100 °C'
        assert q.render(scale='C') == '100 C'
        assert q.render(scale='K') == '373.15 K'
        assert q.render(scale='°F') == '212 °F'
        assert q.render(scale='F') == '212 F'
        #assert q.render(scale='°R') == '671.67 °R'
        #assert q.render(scale='R') == '671.67 R'

        q=Quantity('212 F')
        assert q.render() == '212 F'
        assert q.render(scale='C') == '100 C'
        assert q.render(scale='K') == '373.15 K'
        assert q.render(scale='°C') == '100 °C'
        assert q.render(scale='°F') == '212 °F'
        assert q.render(scale='F') == '212 F'
        #assert q.render(scale='°R') == '671.67 °R'
        #assert q.render(scale='R') == '671.67 R'

        q=Quantity('100 °C', scale='K')
        assert q.render() == '373.15 K'

        q=Quantity('212 °F', scale='K')
        assert q.render() == '373.15 K'

        q=Quantity('212 °F', scale='C')
        assert q.render() == '100 C'

        q=Quantity('212 F', scale='°C')
        assert q.render() == '100 °C'

        q=Quantity('491.67 R', scale='°C')
        assert q.is_close(Quantity('0 °C'))

        q=Quantity('491.67 R', scale='K')
        assert q.render() == '273.15 K'

def test_distance():
    Quantity.reset_prefs()
    with Quantity.prefs(
        spacer=None, show_label=None, label_fmt=None, label_fmt_full=None,
        ignore_sf=False
    ):
        q=Quantity('1_m')
        assert q.render() == '1 m'
        assert q.render(scale='cm', form='eng') == '100 cm'
        assert q.render(scale='mm', form='eng') == '1e3 mm'
        assert q.render(scale='um', form='eng') == '1e6 um'
        assert q.render(scale='μm', form='eng') == '1e6 μm'
        assert q.render(scale='nm', form='eng') == '1e9 nm'
        assert q.render(scale='Å', form='eng') == '10e9 Å'
        assert q.render(scale='angstrom', form='eng') == '10e9 angstrom'
        assert q.render(scale='mi') == '621.37 umi'
        assert q.render(scale='mile') == '621.37 umile'
        assert q.render(scale='miles') == '621.37 umiles'
        assert q.render(scale='in') == '39.37 in'
        assert q.render(scale='inch') == '39.37 inch'
        assert q.render(scale='inches') == '39.37 inches'

        q=Quantity('1_m')
        assert q.render() == '1 m'

        q=Quantity('100cm', scale='m')
        assert q.render() == '1 m'

        q=Quantity('1cm', scale='m')
        assert q.render() == '10 mm'

        q=Quantity('1000mm', scale='m')
        assert q.render() == '1 m'

        q=Quantity('1mm', scale='m')
        assert q.render() == '1 mm'

        q=Quantity('1000000um', scale='m')
        assert q.render() == '1 m'

        q=Quantity('1um', scale='m')
        assert q.render() == '1 um'

        q=Quantity('1000000μm', scale='m')
        assert q.render() == '1 m'

        q=Quantity('1μm', scale='m')
        assert q.render() == '1 um'

        q=Quantity('1000000000nm', scale='m')
        assert q.render() == '1 m'

        q=Quantity('1nm', scale='m')
        assert q.render() == '1 nm'

        q=Quantity('10000000000Å', scale='m')
        assert q.render() == '1 m'

        q=Quantity('1Å', scale='m')
        assert q.render() == '100 pm'

        q=Quantity('1_mi', scale='m')
        assert q.render() == '1.6093 km'

        q=Quantity('1_mile', scale='m')
        assert q.render() == '1.6093 km'

        q=Quantity('1_miles', scale='m')
        assert q.render() == '1.6093 km'

        q=Quantity('d = 93 Mmiles  -- average distance from Sun to Earth', scale='m')
        assert q.render() == '149.67 Gm'

def test_mass():
    Quantity.reset_prefs()
    with Quantity.prefs(
        spacer=None, show_label=None, label_fmt=None, label_fmt_full=None,
        ignore_sf=False
    ):
        q=Quantity('1 g')
        assert q.render() == '1 g'
        assert q.render(scale='oz') == '35.274 moz'
        assert q.render(scale='lb') == '2.2046 mlb'
        assert q.render(scale='lbs') == '2.2046 mlbs'

        q=Quantity('1 oz', scale='g')
        assert q.render() == '28.35 g'

        q=Quantity('1 lb', scale='g')
        assert q.render() == '453.59 g'

        q=Quantity('1 lbs', scale='g')
        assert q.render() == '453.59 g'

def test_time():
    Quantity.reset_prefs()
    with Quantity.prefs(
        spacer=None, show_label=None, label_fmt=None, label_fmt_full=None,
        ignore_sf=True
    ):
        q=Quantity('86400 s')
        assert q.render() == '86.4 ks'
        assert q.render(scale='sec') == '86.4 ksec'
        assert q.render(scale='min') == '1.44 kmin'
        assert q.render(scale='hr') == '24 hr'
        assert q.render(scale='hour') == '24 hour'
        assert q.render(scale='day') == '1 day'

        q=Quantity('1 day', scale='s')
        assert q.render() == '86.4 ks'

        q=Quantity('24 hour', scale='s')
        assert q.render() == '86.4 ks'

        q=Quantity('24 hr', scale='s')
        assert q.render() == '86.4 ks'

        q=Quantity('60 min', scale='s')
        assert q.render() == '3.6 ks'

        q=Quantity('60 sec', scale='s')
        assert q.render() == '60 s'

def test_scale():
    Quantity.reset_prefs()
    secs = Quantity('86400 s')
    days = secs.scale('day')
    assert secs.render() == '86.4 ks'
    assert days.render() == '1 day'

def test_add():
    Quantity.reset_prefs()
    total = Quantity(0, '$')
    for contribution in [1.23, 4.56, 7.89]:
        total = total.add(contribution)
    assert total.render() == '$13.68'
    for contribution in [1.23, 4.56, 8.89]:
        total = total.add(contribution, check_units=True)
    assert total.render() == '$28.36'
    for contribution in [1.23, 4.56, 9.89]:
        total = total.add(Quantity(contribution, '$'), check_units=True)
    assert total.render() == '$44.04'
    try:
        total = total.add(Quantity(contribution, 'lbs'), check_units=True)
        assert False
    except TypeError:
        assert True

def test_linear_conversion():
    Quantity.reset_prefs()
    conversion = UnitConversion('USD', 'BTC', 100000)
    assert str(conversion) == 'USD ← 100000*BTC'

    result = conversion.convert(1, 'BTC', 'USD')
    assert str(result) == '100 kUSD'

    result = conversion.convert(1, 'USD', 'BTC')
    assert str(result) == '10 uBTC'

    result = conversion.convert(from_units='BTC', to_units='USD')
    assert str(result) == '100 kUSD'

    result = conversion.convert(from_units='USD', to_units='BTC')
    assert str(result) == '10 uBTC'

    result = conversion.convert('BTC')
    assert str(result) == '100 kUSD'

    result = conversion.convert('USD')
    assert str(result) == '10 uBTC'

    result = conversion.convert(10)
    assert str(result) == '1 MUSD'

    dollar = Quantity('200000 USD')
    bitcoin = conversion.convert(dollar)
    assert str(bitcoin) == '2 BTC'

    dollar = conversion.convert(bitcoin)
    assert str(dollar) == '200 kUSD'


def test_affine_conversion():
    conversion = UnitConversion('F', 'C', 1.8, 32)
    assert str(conversion) == 'F ← 1.8*C + 32'

    result = conversion.convert(0, 'C', 'F')
    assert str(result) == '32 F'

    result = conversion.convert(32, to_units='C')
    assert str(result) == '0 C'

    result = conversion.convert(32, from_units='F')
    assert str(result) == '0 C'

    with pytest.raises(KeyError) as exception:
        result = conversion.convert(0, from_units='X', to_units='X')
    assert str(exception.value) == "unable to convert to 'X'."
    assert isinstance(exception.value, UnknownConversion)
    assert isinstance(exception.value, QuantiPhyError)
    assert isinstance(exception.value, KeyError)
    assert exception.value.args == ('X',)

    result = conversion.convert(0, to_units='X')
    assert str(result) == '32 F'

    with pytest.raises(KeyError) as exception:
        result = conversion.convert(0, from_units='X')
    assert str(exception.value) == "unable to convert from 'X'."
    assert isinstance(exception.value, UnknownConversion)
    assert isinstance(exception.value, QuantiPhyError)
    assert isinstance(exception.value, KeyError)
    assert exception.value.args == ('X',)

def test_func_converters():
    Quantity.reset_prefs()

    def from_dB(value):
        assert isinstance(value, Quantity)
        return 10**(value/20)

    def to_dB(value):
        assert isinstance(value, Quantity)
        return 20*math.log10(value)

    vconverter = UnitConversion('V', 'dBV', from_dB, to_dB)
    assert str(vconverter) == 'V ← from_dB(dBV), dBV ← to_dB(V)'
    assert str(vconverter.convert(Quantity('100mV'))) == '-20 dBV'
    assert str(vconverter.convert(Quantity('-20dBV'))) == '100 mV'

    aconverter = UnitConversion('A', 'dBA', from_dB, to_dB)
    assert str(aconverter) == 'A ← from_dB(dBA), dBA ← to_dB(A)'
    assert str(aconverter.convert(Quantity('100mA'))) == '-20 dBA'
    assert str(aconverter.convert(Quantity('-20dBA'))) == '100 mA'

    assert '{:pdBV}'.format(Quantity('100mV')) == '-20 dBV'
    assert '{:pdBV}'.format(Quantity('10V')) == '20 dBV'
    assert '{:pV}'.format(Quantity('-20 dBV')) == '0.1 V'
    assert '{:pV}'.format(Quantity('20 dBV')) == '10 V'

    assert '{:pdBA}'.format(Quantity('100mA')) == '-20 dBA'
    assert '{:pdBA}'.format(Quantity('10A')) == '20 dBA'
    assert '{:pA}'.format(Quantity('-20 dBA')) == '0.1 A'
    assert '{:pA}'.format(Quantity('20 dBA')) == '10 A'


def test_subclass_conversion():
    Quantity.reset_prefs()

    class Bitcoin(Quantity):
        units = 'BTC'
        form = 'fixed'
        prec = 2
        show_commas = True

    class Satoshi(Quantity):
        units = 'sat'
        form = 'fixed'
        prec = 3
        show_commas = True

    conversion = UnitConversion(Bitcoin, Satoshi, 1e-8)
    assert str(conversion) == 'BTC ← 1e-08*sat'

    result = conversion.convert(1, 'BTC', 'sat')
    assert str(result) == '100 Msat'

    result = conversion.convert(1, 'sat', 'BTC')
    assert str(result) == '10 nBTC'


def test_parameterized_cconverters():

    # one parameter case
    @UnitConversion.fixture
    def from_molarity(M, mw):
        assert isinstance(M, Quantity)
        assert M.units == 'M'
        return M * mw

    @UnitConversion.fixture
    def to_molarity(g_L, mw):
        assert isinstance(g_L, Quantity)
        assert g_L.units == 'g/L'
        return g_L / mw

    conv = UnitConversion('g/L', 'M', from_molarity, to_molarity)

    # scalar params
    KCl_M = Quantity('1.2 mg/L', scale='M', params=74.55)
    assert KCl_M.render() == '16.097 uM'
    assert KCl_M.render(scale='g/L') == '1.2 mg/L'
    assert str(KCl_M.scale('g/L')) == '1.2 mg/L'

    NaCl_M = Quantity('5.0 mg/L', scale='M', params=58.44277)
    assert NaCl_M.render() == '85.554 uM'
    assert NaCl_M.render(scale='g/L') == '5 mg/L'
    assert str(NaCl_M.scale('g/L')) == '5 mg/L'

    # params as tuple
    KCl_M = Quantity('1.2 mg/L', scale='M', params=(74.55,))
    assert KCl_M.render() == '16.097 uM'
    assert KCl_M.render(scale='g/L') == '1.2 mg/L'
    assert str(KCl_M.scale('g/L')) == '1.2 mg/L'

    NaCl_M = Quantity('5.0 mg/L', scale='M', params=(58.44277,))
    assert NaCl_M.render() == '85.554 uM'
    assert NaCl_M.render(scale='g/L') == '5 mg/L'
    assert str(NaCl_M.scale('g/L')) == '5 mg/L'

    # params as dict
    KCl_M = Quantity('1.2 mg/L', scale='M', params=dict(mw=74.55))
    assert KCl_M.render() == '16.097 uM'
    assert KCl_M.render(scale='g/L') == '1.2 mg/L'
    assert str(KCl_M.scale('g/L')) == '1.2 mg/L'

    NaCl_M = Quantity('5.0 mg/L', scale='M', params=dict(mw=58.44277))
    assert NaCl_M.render() == '85.554 uM'
    assert NaCl_M.render(scale='g/L') == '5 mg/L'
    assert str(NaCl_M.scale('g/L')) == '5 mg/L'

    # two parameter case
    @UnitConversion.fixture
    def to_grams(molarity, vol, mw):
        assert isinstance(molarity, Quantity)
        assert molarity.units == 'M'
        return molarity*vol*mw

    @UnitConversion.fixture
    def to_molarity(mass, vol, mw):
        assert isinstance(mass, Quantity)
        assert mass.units == 'g'
        moles = mass/mw
        return moles/vol

    conv = UnitConversion('g', 'M', to_grams, to_molarity)

    # params as tuple
    KCl_M = Quantity('1.2 g', scale='M', params=(0.25, 74.55))
    assert KCl_M.render() == '64.386 mM'
    assert KCl_M.render(scale='g') == '1.2 g'
    assert str(KCl_M.scale('g')) == '1.2 g'

    NaCl_M = Quantity('5.0 g', scale='M', params=(0.25, 58.44277))
    assert NaCl_M.render() == '342.22 mM'
    assert NaCl_M.render(scale='g') == '5 g'
    assert str(NaCl_M.scale('g')) == '5 g'

    # params as dict
    KCl_M = Quantity('1.2 g', scale='M', params=dict(mw=74.55, vol=0.250))
    assert KCl_M.render() == '64.386 mM'
    assert KCl_M.render(scale='g') == '1.2 g'
    assert str(KCl_M.scale('g')) == '1.2 g'

    NaCl_M = Quantity('5.0 g', scale='M', params=dict(mw=58.44277, vol=0.250))
    assert NaCl_M.render() == '342.22 mM'
    assert NaCl_M.render(scale='g') == '5 g'
    assert str(NaCl_M.scale('g')) == '5 g'


def test_reactivated_cconverters():

    def molarity(mass, H2O, molar_mass):
        # mass in g, H2O in lm, molar_mass in g/mol
        moles = mass/molar_mass
        return 1000*moles/H2O

    g2M_KCl = UnitConversion('M', 'g', molarity(1, 250, 74.55))
    g2M_NaCl = UnitConversion('M', 'g', molarity(1, 250, 58.44277))

    g2M_KCl.activate()
    mass = Quantity('1.2 g')
    assert mass.render() == '1.2 g'
    assert mass.render(scale='M') == '64.386 mM'
    molarity = Quantity('64.386 mM')
    assert molarity.render() == '64.386 mM'
    assert molarity.render(scale='g') == '1.2 g'

    g2M_NaCl.activate()
    mass = Quantity('5.0 g')
    assert mass.render() == '5 g'
    assert mass.render(scale='M') == '342.22 mM'
    molarity = Quantity('342.22 mM')
    assert molarity.render() == '342.22 mM'
    assert molarity.render(scale='g', prec=2) == '5 g'

    g2M_KCl.activate()
    mass = Quantity('1.2 g')
    assert mass.render() == '1.2 g'
    assert mass.render(scale='M') == '64.386 mM'
    molarity = Quantity('64.386 mM')
    assert molarity.render() == '64.386 mM'
    assert molarity.render(scale='g') == '1.2 g'

    g2M_NaCl.activate()
    mass = Quantity('5.0 g')
    assert mass.render() == '5 g'
    assert mass.render(scale='M') == '342.22 mM'
    molarity = Quantity('342.22 mM')
    assert molarity.render() == '342.22 mM'
    assert molarity.render(scale='g', prec=2) == '5 g'



if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.

    defined = dict(globals())
    for k, v in defined.items():
        if callable(v) and k.startswith('test_'):
            print()
            print('Calling:', k)
            print((len(k)+9)*'=')
            v()
