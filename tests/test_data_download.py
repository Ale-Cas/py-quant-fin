"""
Test data_sources module.
"""
from quantfin.market import data_download


def test_yahoo_downloader() -> None:
    # provider = data_download.DataProviders.YAHOO
    prices = data_download.YahooDownloader.get_prices(ticker="AAPL")
    assert not prices.empty
