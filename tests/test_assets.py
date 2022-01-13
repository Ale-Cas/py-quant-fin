"""
Test assets module.
"""
from quantfin.market import assets


def test_stock_init() -> None:
    stock = assets.Stock()
    assert isinstance(stock, assets.Stock)
