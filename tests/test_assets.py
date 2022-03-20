"""
Test assets module.
"""
import os

os.system("/usr/bin/arch -x86_64 /bin/zsh")
from quantfin.market.assets import Asset, Stock


def test_stock_init() -> None:
    stock = Stock()
    assert isinstance(stock, Stock)


def test_stock_repr() -> None:
    stock = Stock()
    assert isinstance(stock, Stock)
