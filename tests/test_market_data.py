"""
Tests market_data module.
"""
from source.market.data_sources import DataProviders
from source.market.investment_universe import InvestmentUniverse
from source.market.market_data import MarketData


def test_init_market_data() -> None:
    mkt = MarketData(
        data_provider=DataProviders(),
        investment_universe=InvestmentUniverse(name="SP500"),
    )
    assert isinstance(mkt, MarketData)
