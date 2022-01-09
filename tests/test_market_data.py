"""
Test market_data module.
"""
from quantfin.market.data_sources import DataProviders
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.market.market_data import MarketData


def test_init_market_data() -> None:
    mkt = MarketData(
        data_provider=DataProviders(),
        investment_universe=InvestmentUniverse(name="SP500"),
    )
    assert isinstance(mkt, MarketData)
