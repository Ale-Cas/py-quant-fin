"""
Tests market_data module.
"""
from source.market.data_sources import DataProviders
from source.market.market_data import MarketData


def test_init_market_data() -> None:
    mkt = MarketData(data_provider=DataProviders())
    assert isinstance(mkt, MarketData)
