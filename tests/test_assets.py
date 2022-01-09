"""
Test assets module.
"""
from quantfin.market.assets import Asset, Stock, Bond, ETF


def test_asset_init() -> None:
    asset = Asset()
    assert isinstance(asset, Asset)


def test_stock_init() -> None:
    stock = Stock()
    assert isinstance(stock, Stock)


def test_bond_init() -> None:
    bond = Bond()
    assert isinstance(bond, Bond)


def test_etf_init() -> None:
    etf = ETF()
    assert isinstance(etf, ETF)
