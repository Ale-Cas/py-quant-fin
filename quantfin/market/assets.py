"""Abstraction layer for Assets."""
from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import Optional
from warnings import warn

import pandas as pd
import yfinance as yf


@dataclasses.dataclass
class Cash:
    """This class represents Cash."""

    value: float = 1.0
    currency: str = "EUR"


class Asset(ABC):
    """
    This is an abstact class that represents a single asset.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        asset_class: Optional[str] = None,
        prices: Optional[pd.DataFrame] = None,
    ) -> None:
        """
        Initialize the Asset.
        """
        self.name = name
        self.ticker = ticker
        self.isin = isin
        self.exchange = exchange
        self.asset_class = asset_class
        self.prices = prices

    def __str__(self) -> str:
        return str(self.name or self.ticker or "Asset without name nor ticker")

    def __repr__(self) -> str:
        return str(self.name or self.ticker or "Asset without name nor ticker")

    def __hash__(self) -> int:
        return hash(self.ticker)

    @abstractmethod
    def is_in_index(self):
        """Checks if an asset is part of the specified index"""
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def is_in_universe(self):
        """Checks if an asset is part of the specified InvestmentUniverse"""
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def is_in_portfolio(self):
        """Checks if an asset is part of the specified Portfolio"""
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def get_prices(
        self,
        data_source: str,
        **kwargs,
    ):
        """
        Get historical prices from the specified data source.
        """
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def get_weight_in_portfolio(self):
        """Retrieves the weight of the Asset in the specified Portfolio"""
        raise NotImplementedError("This is an abstract method")


class Stock(Asset):
    """
    This class represent a single Stock.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        prices: Optional[pd.DataFrame] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> None:
        """
        Initialize the Stock
        """
        super().__init__(
            name,
            ticker,
            isin,
            exchange,
            asset_class="Equity",
            prices=prices,
        )
        self.sector = sector
        self.industry = industry

    def __str__(self) -> str:
        return str(self.name or self.ticker or "Asset without name nor ticker")

    def __repr__(self) -> str:
        return str(self.name or self.ticker or "Asset without name nor ticker")

    def __hash__(self) -> int:
        return hash(self.ticker)

    def get_prices(
        self,
        data_source: str = "Yahoo Finance",
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
        if data_source == "Yahoo Finance":

            if self.prices is not None:
                warn("Warning: prices DataFrame has already been defined!")

            if not kwargs:
                self.prices = yf.Ticker(self.ticker).history(
                    period="max",
                    interval="1d",
                )
            else:
                self.prices = yf.Ticker(self.ticker).history(**kwargs)
        else:
            raise NotImplementedError
        return self.prices

    def is_in_index(self):
        """Checks if an asset is part of the specified index"""
        raise NotImplementedError("Not yet implemented")

    def is_in_universe(self):
        """Checks if an asset is part of the specified InvestmentUniverse"""
        raise NotImplementedError("Not yet implemented")

    def is_in_portfolio(self):
        """Checks if an asset is part of the specified Portfolio"""
        raise NotImplementedError("Not yet implemented")

    def get_weight_in_portfolio(self):
        """Retrieves the weight of the Asset in the specified Portfolio"""
        raise NotImplementedError("Not yet implemented")
