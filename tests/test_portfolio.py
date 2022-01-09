"""
Test portfolio module.
"""
from quantfin.portfolio_selection.portfolio import Portfolio


def test_portfolio() -> None:
    ptf = Portfolio()
    assert isinstance(ptf, Portfolio)
