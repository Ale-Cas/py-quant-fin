import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

import pandas as pd

from quantfin.market.investment_universe import (
    MarketIndex,
    InvestmentUniverse,
    PriceType,
)


def test_empty_universe() -> None:
    """InvestmentUniverse can be instantiated without any argument."""
    empty_univ = InvestmentUniverse()
    assert isinstance(empty_univ, InvestmentUniverse)
    with pytest.raises(AssertionError) as assertion:
        empty_univ.assets
        empty_univ.tickers
        empty_univ.prices
        empty_univ.returns
    assert str(assertion.value) == "You must provide a reference_index first!"


def test_custom_tickers() -> None:
    """Users can provide custom tickers to InvestmentUniverse."""
    cst_tickers = ["AAPL", "GOOG", "MSFT"]
    univ = InvestmentUniverse(tickers=cst_tickers)
    assert isinstance(univ.tickers, set) and isinstance(
        univ.assets, set
    ), """
    tickers and assets must be of type: set.
    """
    assert len(univ.tickers) == len(cst_tickers) and len(univ.assets) == len(
        cst_tickers
    ), """
    tickers and assets must have length equal to the one provided by the user.
    """


def test_prices_of_custom_tickers() -> None:
    """Download prices of custom tickers."""
    cst_tickers = ["AAPL", "GOOG", "MSFT", "TSLA"]
    univ = InvestmentUniverse(tickers=cst_tickers)
    assert isinstance(univ.prices, pd.DataFrame)
    assert not univ.prices.empty
    assert len(univ.tickers) == len(cst_tickers) and len(univ.assets) == len(
        cst_tickers
    ), """
    tickers and assets must have length equal to the one provided by the user.
    """


def test_prices_of_reference_index_universe() -> None:
    """Download prices of reference index components."""
    univ = InvestmentUniverse(reference_index=MarketIndex.NASDAQ100.value)
    assert isinstance(univ.prices, pd.DataFrame)
    assert not univ.prices.empty


def test_returns_of_reference_index_universe() -> None:
    """Download prices of reference index components."""
    univ = InvestmentUniverse(reference_index=MarketIndex.NASDAQ100.value)
    assert isinstance(univ.returns, pd.DataFrame)
    assert not univ.returns.empty


def test_reference_index_universe_with_custom_dates() -> None:
    univ = InvestmentUniverse(reference_index=MarketIndex.NASDAQ100.value)
    start_date = str(date.today() - relativedelta(years=3))
    end_date = str(date.today())
    univ.get_prices(price_type=PriceType.CLOSE.value, start=start_date, end=end_date)
    assert isinstance(univ.prices, pd.DataFrame)
    assert not univ.prices.empty


def test_universe_with_custom_tickers_and_dates() -> None:
    cst_tickers = ["AAPL", "GOOG", "MSFT"]
    univ = InvestmentUniverse(tickers=cst_tickers)
    start_date = "2015-01-22"
    end_date = "2021-01-22"
    univ.get_prices(price_type=PriceType.CLOSE.value, start=start_date, end=end_date)
    assert isinstance(univ.prices, pd.DataFrame)
    assert not univ.prices.empty
