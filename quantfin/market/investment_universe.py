"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Union
from warnings import warn

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

from quantfin.utils import ListEnum
from quantfin.market.assets import Stock


class MarketIndex(str, ListEnum):
    """List of supported indexes."""

    SP500 = "S&P 500"
    NASDAQ100 = "NASDAQ 100"


class PriceType(str, ListEnum):
    """List of supported prices."""

    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"


def scrape_largest_companies(num_pages: int = 58) -> pd.DataFrame:
    """Scrapes name, ticker symbols and country of top companies based on market cap.

    Parameters
    ----------
    num_pages: int
        number of pages to scrape, each page has 100 symbols, max is

    Returns
    -------
        A pandas DataFrame
    """
    list_tickers: List[str] = []
    list_names: List[str] = []
    list_countries: List[str] = []
    for num_page in range(num_pages):
        url = f"https://companiesmarketcap.com/page/{num_page+1}/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        list_ticker_page = [e.text for e in soup.select("div.company-code")]
        list_names_page = [e.text for e in soup.select("div.company-name")]
        list_countries_page = [e.text for e in soup.select("span.responsive-hidden")]
        list_countries_page = list_countries_page[1:]
        list_tickers = list_tickers + list_ticker_page
        list_names = list_names + list_names_page
        list_countries = list_countries + list_countries_page
        companies_dict = {
            "ticker": list_tickers,
            "name": list_names,
            "country": list_countries,
        }

    return pd.DataFrame(companies_dict, columns=companies_dict.keys())


class InvestmentUniverse:
    """
    This class represent an investment universe.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        reference_index: Optional[Union[str, MarketIndex]] = None,
        countries: Optional[List[str]] = None,
        assets: Optional[Set[Stock]] = None,
        prices: Optional[pd.DataFrame] = None,
    ) -> None:
        self.name = name
        if reference_index in MarketIndex.list():
            self.reference_index = reference_index
        else:
            raise ValueError(
                f"""Inappropriate universe name, 
                supported universe names are: {",".join(MarketIndex.list())}"""
            )
        self.countries = countries
        self.assets = assets or self.get_assets()
        self.prices = prices or pd.DataFrame()

    def get_assets(
        self,
    ) -> Set[Stock]:
        """
        Get assets in the universe.

        Returns
        -------
        self.assets
            A set[Stock]
        """
        self.assets = set()
        if self.reference_index == MarketIndex.SP500.value:
            sp500_tickers: List = pd.read_html(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )[0]["Symbol"].tolist()
            for ticker in sp500_tickers:
                self.assets.add(Stock(ticker=ticker))
        if self.reference_index == MarketIndex.NASDAQ100.value:
            nasdaq100_tickers = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[
                3
            ]["Ticker"].tolist()
            for ticker in nasdaq100_tickers:
                self.assets.add(Stock(ticker=ticker))
        return self.assets

    def get_prices(
        self,
        prices_column: Optional[str] = None,
        **kwargs,
    ) -> Union[Dict[Stock, pd.DataFrame], pd.DataFrame]:
        """
        Get historical prices from Yahoo Finance.

        Parameters
        ----------
        prices_column: Optional[str]
            Valid columns: "Open","High","Low","Close","Volume"
            If you want to see also "Dividends","Stock Splits"
            Please put actions=True
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime.
            Default is 1900-01-01
        end: str
            Download end date string (YYYY-MM-DD) or _datetime.
            Default is now
        group_by : str
            Group by 'ticker' or 'column' (default)
        prepost : bool
            Include Pre and Post market data in results?
            Default is False
        auto_adjust: bool
            Adjust all OHLC automatically? Default is True
        actions: bool
            Download dividend + stock splits data. Default is False
        threads: bool / int
            How many threads to use for mass downloading. Default is True
        proxy: str
            Optional. Proxy server URL scheme. Default is None
        rounding: bool
            Optional. Round values to 2 decimal places?
        show_errors: bool
            Optional. Doesn't print errors if True
        timeout: None or float
            If not None stops waiting for a response after given number of
            seconds. (Can also be a fraction of a second e.g. 0.01)

        Returns
        -------
        prices
            A pd.DataFrame containing historical prices for the specified parameters
        """
        if not kwargs:
            self.prices = yf.download(
                tickers=[str(asset.ticker) for asset in self.assets],
                group_by="Ticker",
                period="max",
                auto_adjust=True,
            )
        else:
            self.prices = yf.download(
                tickers=[str(asset.ticker) for asset in self.assets],
                group_by="Ticker",
                **kwargs,
            )
        if prices_column is not None:
            if prices_column not in PriceType.list():
                message = (
                    "Warning: Please provide a column name, "
                    + f"valid ones are: {PriceType.list()}, "
                    + "otherwise will be ignored"
                )
                warn(message=message)
            else:
                self.prices = self.prices.xs(prices_column, level=1, axis=1)

        return self.prices
