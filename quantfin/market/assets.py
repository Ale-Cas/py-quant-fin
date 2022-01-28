"""Abstraction layer for Assets."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

import pandas as pd

from quantfin.utils import ListEnum

if TYPE_CHECKING:
    from quantfin.portfolio_selection.portfolio import Portfolio


class Currencies(str, ListEnum):
    """List of supported currencies."""

    EUR = "EUR"
    USD = "USD"

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)


class AssetClasses(str, ListEnum):
    """List of supported asset classes."""

    STOCKS = "Stocks"
    BONDS = "Bonds"
    ETF = "Exchange Traded Funds"
    CURRENCIES = "Currencies"


class Asset(ABC):
    """
    This is an interface (abstact class) that represents a single asset.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        asset_class: Optional[AssetClasses] = None,
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
        return str(self.ticker)

    def __repr__(self) -> str:
        return str(self.ticker)

    def __hash__(self) -> int:
        return hash(self.ticker)

    def __eq__(self, other: Asset):
        return (self.ticker) == (other.ticker)

    def __ne__(self, other: Asset):
        return not (self == other)

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


class Cash(Asset):
    """This class represents Cash."""

    def __init__(self, currency: Currencies = Currencies.EUR.value) -> None:
        self.currency = currency

    def __repr__(self) -> str:
        return str(self.currency)

    def __str__(self) -> str:
        return str(f"Cash in {self.currency}")

    def __hash__(self) -> int:
        return hash(str(self.currency))

    def __eq__(self, other: Cash):
        return (self.currency) == (other.currency)

    def __ne__(self, other):
        return not (self == other)

    def is_in_portfolio(self, portfolio: Portfolio) -> bool:
        """Checks if cash is part of the specified Portfolio"""
        if self in portfolio.nonzero_holdings:
            return True
        else:
            return False

    def get_weight_in_portfolio(self, portfolio: Portfolio) -> float:
        """Retrieves the weight of the Asset in the specified Portfolio"""
        if self in portfolio.nonzero_holdings:
            return portfolio.nonzero_holdings[self]
        else:
            return 0.0

    def is_in_index(self):
        """Checks if an asset is part of the specified index"""
        raise NotImplementedError("This method does not apply to cash")

    def is_in_universe(self):
        """Checks if an asset is part of the specified InvestmentUniverse"""
        raise NotImplementedError("This method does not apply to cash")


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
        country: Optional[str] = None,
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
            asset_class=AssetClasses.STOCKS,
            prices=prices,
        )
        self.country = country
        self.sector = sector
        self.industry = industry

    def is_in_index(self):
        """Checks if an asset is part of the specified index"""
        raise NotImplementedError("Not yet implemented")

    def is_in_universe(self):
        """Checks if an asset is part of the specified InvestmentUniverse"""
        raise NotImplementedError("Not yet implemented")

    def is_in_portfolio(self, portfolio: Portfolio) -> bool:
        """Checks if an asset is part of the specified Portfolio"""
        if self in portfolio.nonzero_holdings:
            return True
        else:
            return False

    def get_weight_in_portfolio(self, portfolio: Portfolio) -> bool:
        """Retrieves the weight of the Asset in the specified Portfolio"""
        if self in portfolio.nonzero_holdings:
            return portfolio.nonzero_holdings[self]
        else:
            return 0.0
