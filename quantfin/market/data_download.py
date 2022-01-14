"""
The data download module implements a strategy design 
to download market data from different data providers.
"""
from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd
import yfinance as yf


class DataProviders(Enum):
    """Enum of supported data providers."""

    YAHOO = "Yahoo Finance"
    ALPACA = "Alpaca API"
    STOOQ = "Stooq"


class IDataDownloader(ABC):
    """Interface for data downloading."""

    @staticmethod
    @abstractmethod
    def get_prices(
        ticker: str,
        **kwargs,
    ):
        """Get historical prices for the asset."""
        raise NotImplementedError("This is an abstract method")


class YahooDownloader(IDataDownloader):
    """Concrete class to download data from yahoo finance."""

    @staticmethod
    def get_prices(
        ticker: str,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get historical prices from the specified data source.

        Parameters
        ----------
        data_source: str
            Valid data sources: Yahoo Finance (default)
        You can specify additional parameters, depending on the data_source

        Returns
        -------
        prices
            A pandas DataFrame containing historical prices for specified parameters
        """
        if not kwargs:
            prices = yf.Ticker(ticker).history(
                period="max",
                interval="1d",
            )
        else:
            prices = yf.Ticker(ticker).history(**kwargs)
        return prices
