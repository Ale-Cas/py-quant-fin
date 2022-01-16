"""Abstraction layer for Assets."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import pandas as pd

from quantfin.utils import ListEnum

if TYPE_CHECKING:
    from quantfin.market.data_download import DataProviders


class AssetClasses(str, ListEnum):
    STOCKS = "Stocks"
    BONDS = "Bonds"
    ETFs = "Exchange Traded Funds"
    CURRENCIES = "Currencies"


class Indexes(str, ListEnum):
    SP500 = "S&P 500"
    NASDAQ100 = "NASDAQ 100"


class IAsset(ABC):
    """
    This is an interface (abstact class) that represents a single asset.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        asset_class: Optional[str] = None,
        data_provider: Optional[DataProviders] = None,
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
        self.data_provider = data_provider
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
    def get_weight_in_portfolio(self):
        """Retrieves the weight of the Asset in the specified Portfolio"""
        raise NotImplementedError("This is an abstract method")


@dataclass
class Cash(IAsset):
    """This class represents Cash."""

    value: float = 1.0
    currency: str = "EUR"

    def __hash__(self) -> int:
        return hash(self.currency)

    def __str__(self) -> str:
        return "Cash"

    def __repr__(self) -> str:
        return "Cash"

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


class Stock(IAsset):
    """
    This class represent a single Stock.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        data_provider: Optional[DataProviders] = None,
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
            data_provider=data_provider,
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
