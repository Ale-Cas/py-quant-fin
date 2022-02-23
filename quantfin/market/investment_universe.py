"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations

from typing import List, Optional, Set, Union

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

from quantfin.utils import ListEnum
from quantfin.market.assets import Asset, Stock


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
        tickers: Union[str, Set[str], List[str]] = None,
        assets: Optional[Set[Asset]] = None,
        bars: Optional[pd.DataFrame] = None,
        prices: Optional[pd.DataFrame] = None,
        returns: Optional[pd.DataFrame] = None,
    ) -> None:
        self.name = name
        self.reference_index = reference_index
        if self.reference_index:
            assert (
                self.reference_index in MarketIndex.list()
            ), f"""Inappropriate universe name, 
                 supported universe names are: {", ".join(MarketIndex.list())}"""
        if tickers is not None:
            self._tickers = set(tickers)
        else:
            self._tickers = tickers
        if assets is not None:
            self._assets = set(assets)
        else:
            self._assets = assets
        self._bars = bars or pd.DataFrame()
        self._prices = prices or pd.DataFrame()
        self._returns = returns or pd.DataFrame()

    def get_tickers(self) -> Set[str]:
        """
        Get tickers for each asset in the universe.

        Returns
        -------
        self.tickers
            A set[Asset]
        """
        if self._tickers is None:
            assert self.reference_index, "You must provide a reference_index first!"
            self._tickers = set()
            if self.reference_index == MarketIndex.SP500.value:
                sp500_tickers: List = pd.read_html(
                    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
                )[0]["Symbol"].tolist()
                self._tickers = set(sp500_tickers)
            if self.reference_index == MarketIndex.NASDAQ100.value:
                nasdaq100_tickers = pd.read_html(
                    "https://en.wikipedia.org/wiki/Nasdaq-100"
                )[3]["Ticker"].tolist()
                self._tickers = set(nasdaq100_tickers)
        return self._tickers

    def set_tickers(self, tickers: Union[str, Set[str], List[str]]) -> None:
        assert isinstance(
            tickers, (str, Set[str], List[str])
        ), """
            Please provide a string, set or list of tickers.
            """
        self._tickers = set(tickers)

    tickers = property(fget=get_tickers, fset=set_tickers)

    def get_assets(
        self,
    ) -> Set[Asset]:
        """
        Get assets in the universe.

        Returns
        -------
        self.assets
            A set[Asset]
        """
        # if there are tickers then use them
        if self.tickers:
            self._assets = set()
            for ticker in self.tickers:
                self._assets.add(Stock(ticker=ticker))
        elif self._assets is None:
            assert self.reference_index, "You must provide a reference_index first!"
            self._assets = set()
            if self.reference_index == MarketIndex.SP500.value:
                sp500_tickers: List = pd.read_html(
                    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
                )[0]["Symbol"].tolist()
                for ticker in sp500_tickers:
                    self._assets.add(Stock(ticker=ticker))
            if self.reference_index == MarketIndex.NASDAQ100.value:
                nasdaq100_tickers = pd.read_html(
                    "https://en.wikipedia.org/wiki/Nasdaq-100"
                )[3]["Ticker"].tolist()
                for ticker in nasdaq100_tickers:
                    self._assets.add(Stock(ticker=ticker))
        return self._assets

    def set_assets(self, assets: Union[Set[Asset], List[Asset]]) -> None:
        for asset in assets:
            assert isinstance(
                asset, Asset
            ), "Please provide a list or set of Asset objects."
        self._assets = assets

    assets = property(fget=get_assets, fset=set_assets)

    def get_bars(
        self,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get historical prices from Yahoo Finance.

        Parameters
        ----------
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Default = "max"
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
            Group by 'ticker' (default) or 'column'
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
            A pd.DataFrame containing historical bars for the specified parameters
        """
        if self._bars.empty:
            if not kwargs:
                self._bars = yf.download(
                    tickers=self.tickers,
                    group_by="Ticker",
                    period="max",
                    auto_adjust=True,
                )
            else:
                self._bars = yf.download(
                    tickers=self.tickers,
                    group_by="Ticker",
                    auto_adjust=True,
                    **kwargs,
                )
        return self._bars

    def set_bars(self, bars: pd.DataFrame) -> None:
        if isinstance(bars, pd.DataFrame):
            self._bars = bars
        else:
            raise ValueError("Prices must be a pandas DataFrame.")

    bars = property(fget=get_bars, fset=set_bars)

    def get_prices(
        self, price_type: PriceType = PriceType.CLOSE, **kwargs
    ) -> pd.DataFrame:
        if self._prices.empty:
            assert isinstance(
                price_type, (PriceType, str)
            ), """
            Provide a valid price_type. Valid ones are PriceType or str.
            """
            assert (
                price_type in PriceType.list()
            ), f"""
            Provide a valid price_type. Valid ones are {", ".join(PriceType.list())}.
            """
            if self._bars.empty:
                self._bars = self.get_bars(**kwargs)
            elif kwargs:
                self._bars = self.get_bars(**kwargs)
            self._prices: pd.DataFrame = self._bars.xs(price_type, level=1, axis=1)

        return self._prices

    def set_prices(self, prices: pd.DataFrame) -> None:
        if isinstance(prices, pd.DataFrame):
            self._prices = prices
        else:
            raise ValueError("Prices must be a pandas DataFrame.")

    prices = property(fget=get_prices, fset=set_prices)

    def get_returns(
        self,
        required_pct_obs: float = 0.7,
        price_type: PriceType = PriceType.CLOSE,
        **kwargs,
    ) -> pd.DataFrame:
        if self._returns.empty:
            if self._prices.empty:
                self._prices = self.get_prices(price_type=price_type, **kwargs)
            returns: pd.DataFrame = self._prices.pct_change().iloc[1:, :]
            self._returns = returns.dropna(
                axis=1, thresh=int(len(returns) * required_pct_obs)
            ).fillna(0.0)
        return self._returns

    def set_returns(self, returns: pd.DataFrame) -> None:
        if isinstance(returns, pd.DataFrame):
            self._returns = returns
        else:
            raise ValueError("Prices must be a pandas DataFrame.")

    returns = property(fget=get_returns, fset=set_returns)

    @property
    def num_tot_assets(self) -> int:
        return len(self.assets)

    @property
    def num_ret_assets(self) -> int:
        return len(self.returns.columns)

    @property
    def num_obs_prices(self) -> int:
        return len(self.prices.index)

    @property
    def num_obs_returns(self) -> int:
        return len(self.returns.index)
