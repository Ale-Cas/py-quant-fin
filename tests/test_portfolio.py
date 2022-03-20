"""
Test portfolio module.
"""
import os

os.system("/usr/bin/arch -x86_64 /bin/zsh")
import pytest
from quantfin.market import assets
from quantfin.portfolio_selection import portfolio


def test_empty_portfolio() -> None:
    ptf = portfolio.Portfolio()
    assert isinstance(ptf, portfolio.Portfolio)


def test_portfolio_with_holdings() -> None:
    ptf = portfolio.Portfolio(
        holdings={
            assets.Stock(ticker="AAPL"): 0.3,
            assets.Stock(ticker="MSFT"): 0.3,
        }
    )
    assert isinstance(ptf, portfolio.Portfolio)


def test_multiple_portfolios() -> None:
    empty_ptf = portfolio.Portfolio()
    ptf = portfolio.Portfolio(
        holdings={
            assets.Stock(ticker="AAPL"): 0.3,
            assets.Stock(ticker="TSLA"): 0.2,
            assets.Stock(ticker="MSFT"): 0.1,
        }
    )


def test_portfolio_assertions() -> None:
    def sum_weights_assertion_error() -> None:
        ptf = portfolio.Portfolio(
            holdings={
                assets.Stock(ticker="AAPL"): 0.3,
                assets.Stock(ticker="TSLA"): 0.2,
                assets.Stock(ticker="MSFT"): 0.6,
            }
        )
        assert isinstance(ptf, portfolio.Portfolio)

    with pytest.raises(AssertionError):
        sum_weights_assertion_error()
