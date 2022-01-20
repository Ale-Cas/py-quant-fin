"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Union
from warnings import warn

import pandas as pd
import yfinance as yf

from quantfin.market.assets import Indexes, Stock


class InvestmentUniverse:
    """
    This class represent an investment universe.
    """

    def __init__(
        self,
        name: str,
        assets: Optional[Set[Stock]] = None,
        prices: pd.DataFrame = None,
    ) -> None:
        if name in Indexes.list():
            self.name = name
        else:
            raise ValueError(
                f"""Inappropriate universe name, 
                supported universe names are: {",".join(Indexes.list())}"""
            )
        self.assets = assets or self.get_assets()
        self.prices = prices or pd.DataFrame()

    def get_assets(
        self,
        source: str = "Wikipedia",
    ) -> Set[Stock]:
        """
        Get historical prices from the data source specified during the initialisation.

        Parameters
        ----------
        source : str
                Valid sources: Wikipedia

        Returns
        -------
        self.assets
            A set[Stock]
        """
        VALID_SOURCES = {"Wikipedia"}  # pylint: disable=invalid-name
        if source not in VALID_SOURCES:
            raise ValueError(
                f"""The source is not valid, supported ones are: {VALID_SOURCES}"""
            )
        self.assets = set()
        if self.name == Indexes.SP500.value:
            sp500_tickers: List = pd.read_html(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )[0]["Symbol"].tolist()
            for ticker in sp500_tickers:
                self.assets.add(Stock(ticker=ticker))
        if self.name == Indexes.NASDAQ100.value:
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
        Get historical prices from the data source specified during the initialisation.

        Parameters
        ----------
        prices_column: Optional[str]
            Valid columns: "Open","High","Low","Close","Volume"
            If you want to see also "Dividends","Stock Splits"
            Please put actions=True
        tickers : str, list
            List of tickers to download
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
        VALID_PRICE_COLUMNS = {  # pylint: disable=invalid-name
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Dividends",
            "Stock Splits",
        }
        _valid_arguments = {
            "tickers",
            "period",
            "interval",
            "start",
            "end",
            "group_by",
            "actions",
            "prepost",
            "auto_adjust",
            "proxy",
            "rounding",
            "show_errors",
            "timeout",
        }
        if not self.prices.empty:
            warn("Warning: prices has already been defined!")

        if not kwargs:
            self.prices = yf.download(
                tickers=[str(asset) for asset in self.assets],
                group_by="Ticker",
                period="max",
                auto_adjust=True,
            )
        else:
            for key in kwargs:
                if key in _valid_arguments:
                    self.prices = yf.download(
                        tickers=[str(asset) for asset in self.assets],
                        **kwargs,
                    )
                else:
                    message = f"""Warning: Please provide a valid keyword, 
                         valid ones are: {_valid_arguments}, 
                         otherwise will be ignored"""
                    warn(message=message)
        if prices_column is not None:
            if prices_column not in VALID_PRICE_COLUMNS:
                warn(
                    f"""Warning: price_column not supported,
                    must be one of: {VALID_PRICE_COLUMNS},
                    otherwise will be like the argument was not provided"""
                )
            else:
                self.prices = self.prices.xs(prices_column, level=1, axis=1)

        return self.prices
