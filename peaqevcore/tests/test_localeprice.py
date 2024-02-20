import pytest
from ..models.locale.price.locale_price import LocalePrice
from ..models.locale.price.models.seasoned_price import SeasonedPrice
from ..models.locale.price.models.tiered_price import TieredPrice
from ..models.locale.enums.price_type import PriceType

_linja_tiers = [TieredPrice(upper_peak_limit=2,value=263,),
                TieredPrice(upper_peak_limit=5,value=329,),
                TieredPrice(upper_peak_limit=10,value=395,),
                TieredPrice(upper_peak_limit=15,value=658,),
                TieredPrice(upper_peak_limit=20,value=789,),
                TieredPrice(upper_peak_limit=25,value=920,),
                TieredPrice(upper_peak_limit=50,value=1315,),
                TieredPrice(upper_peak_limit=75,value=1446,),
                TieredPrice(upper_peak_limit=100,value=1578,),
                TieredPrice(upper_peak_limit=999,value=1973,)]

@pytest.fixture
def localeprice():
    return LocalePrice()

def test_single_peak(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [100.0]
    tiers = [TieredPrice(upper_peak_limit=150.0, value=0)]
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 149.9


def test_multiple_peaks_same_value(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [100.0, 100.0, 100.0]
    tiers = [TieredPrice(upper_peak_limit=150.0, value=0)]
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 149.9


def test_multiple_peaks_almost_same_value(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [100.0, 100.0, 99.6]
    tiers = [TieredPrice(upper_peak_limit=150.0, value=0)]
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 149.9


def test_multiple_peaks_almost_two_min(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [100.0, 99.5, 99.6]
    tiers = [TieredPrice(upper_peak_limit=150.0, value=0)]
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 149.9


def test_multiple_peaks_different_values(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [100.0, 110.0, 120.0]
    tiers = [TieredPrice(upper_peak_limit=150.0, value=0)]
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 149.9


def test_multiple_peaks_multiple_tiers(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [100.0, 110.0, 120.0]
    tiers = [TieredPrice(upper_peak_limit=105.0, value=0), TieredPrice(upper_peak_limit=115.0, value=0), TieredPrice(upper_peak_limit=125.0, value=0)]
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 112.3


def test_realcase1(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [0.05, 14.6, 14.6]
    tiers = _linja_tiers
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 0.5
    

def test_realcase2(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [2.05,2.7,2.81]
    tiers = _linja_tiers
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 4.9


def test_realcase3(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [0.01, 0.01, 12.5]
    tiers = _linja_tiers
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 1.1


def test_realcase4(localeprice):
    localeprice.price_type = PriceType.Tiered
    peaks = [2.7]
    tiers = _linja_tiers
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == 4.9


def test_price_type_not_tiered(localeprice):
    localeprice.price_type = PriceType.Static
    peaks = [100.0, 110.0, 120.0]
    tiers = []
    result = localeprice.get_observed_peak(peaks, tiers)
    assert result == sum(peaks) / len(peaks)