from datetime import date
from dateutil.relativedelta import relativedelta
from quantfin.market.investment_universe import (
    MarketIndex,
    InvestmentUniverse,
    PriceType,
)


def test_inv_univ() -> None:
    univ = InvestmentUniverse(reference_index=MarketIndex.NASDAQ100.value)
    univ.get_prices(prices_column=PriceType.CLOSE.value)
    assert not univ.prices.empty


def test_inv_univ_with_custom_dates() -> None:
    univ = InvestmentUniverse(reference_index=MarketIndex.NASDAQ100.value)
    start_date = str(date.today() - relativedelta(years=3))
    end_date = str(date.today())
    univ.get_prices(prices_column=PriceType.CLOSE.value, start=start_date, end=end_date)
    assert not univ.prices.empty
