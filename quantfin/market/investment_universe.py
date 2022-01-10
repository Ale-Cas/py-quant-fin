"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Union
from warnings import warn
import pandas as pd

from quantfin.market.assets import Asset


class InvestmentUniverse:
    """
    This class represent an investment universe.
    """

    VALID_UNIVERSE_NAMES: set = {"SP500", "NASDAQ100"}

    def __init__(
        self,
        name: str,
        assets: Optional[Set[Asset]] = None,
        prices: Optional[Union[Dict[Asset, pd.DataFrame], pd.DataFrame]] = None,
    ) -> None:
        if name in InvestmentUniverse.VALID_UNIVERSE_NAMES:
            self.name = name
        else:
            raise ValueError(
                f"""Inappropriate universe name, 
                supported universe names are: {InvestmentUniverse.VALID_UNIVERSE_NAMES}"""
            )
        self.assets = assets or self._get_assets()
        self.prices = prices

    def _get_assets(
        self,
        source: str = "Wikipedia",
    ) -> Set[Asset]:
        VALID_SOURCES = {"Wikipedia"}  # pylint: disable=invalid-name
        if source not in VALID_SOURCES:
            raise ValueError(
                f"""The source is not valid, supported ones are: {VALID_SOURCES}"""
            )
        self.assets = set()
        if self.name == "SP500":
            sp500_tickers: List = pd.read_html(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )[0]["Symbol"].tolist()
            for ticker in sp500_tickers:
                self.assets.add(Asset(ticker=ticker))
        if self.name == "NASDAQ100":
            nasdaq100_tickers = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[
                3
            ]["Ticker"].tolist()
            for ticker in nasdaq100_tickers:
                self.assets.add(Asset(ticker=ticker))
        return self.assets

    def get_prices(
        self,
        prices_column: Optional[str] = None,
        **kwargs,
    ) -> Union[Dict[Asset, pd.DataFrame], pd.DataFrame]:
        """
        Get historical prices from the data source specified during the initialisation.

        Parameters
        ----------
        period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or pd.Timestamp.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or pd.Timestamp.
                Default is now
            actions: bool
                Include columns Dividends & Asset Splits?
                Default is True
            prepost: bool
                Include Pre and Post market data in results?
                Default is False
            auto_adjust: bool
                Adjust all OHLC automatically? Default is True
            back_adjust: bool
                Back-adjusted data to mimic true historical prices (optional)
            prices_column: optional[str]
                Column from stock prices DataFrame that we want to retrieve

        Returns
        -------
        prices
            A dict[Asset:DataFrame] or a pandas DataFrame containing historical prices for specified parameters
        """
        VALID_PRICE_COLUMNS = {  # pylint: disable=invalid-name
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Dividends",
            "Asset Splits",
        }
        _valid_arguments = {
            "period",
            "interval",
            "start",
            "end",
            "actions",
            "prepost_data",
            "auto_adjust",
            "back_adjust",
        }
        if self.prices:
            warn("Warning: prices has already been defined!")

        if not kwargs:
            self.prices = {asset.ticker: asset.get_prices() for asset in self.assets}
        else:
            for key in kwargs:
                if key in _valid_arguments:
                    self.prices = {
                        asset.ticker: asset.get_prices(**kwargs) for asset in self.assets
                    }
        # now I already have self.prices = {Asset.ticker: pd.DataFrame}
        # TODO: Take data from the first available date
        if prices_column is not None:
            if prices_column not in VALID_PRICE_COLUMNS:
                warn(
                    f"""Warning: price_column not supported,
                    must be one of: {VALID_PRICE_COLUMNS},
                    otherwise will be like the argument was not provided"""
                )
            else:
                for asset in self.assets:
                    min_date = pd.Timestamp("1990-01-01")
                    if min(self.prices[str(asset)].index) < min_date:
                        min_date = min(self.prices[str(asset)].index)
                        min_date_asset = asset
                self.prices[min_date_asset] = self.prices[str(min_date_asset)][
                    prices_column
                ]
                for asset in self.assets:
                    self.prices[asset] = self.prices[str(asset)]["Close"]

                return self.prices

        return self.prices
