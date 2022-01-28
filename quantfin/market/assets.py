"""Abstraction layer for Assets."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

import pandas as pd

from quantfin.utils import ListEnum

if TYPE_CHECKING:
    from quantfin.portfolio_selection.portfolio import Portfolio


class Currency(str, ListEnum):
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Asset):
            return NotImplemented
        return (self.ticker) == (other.ticker)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Asset):
            return NotImplemented
        return not self == other

    @abstractmethod
    def is_in_index(self):
        """Checks if an asset is part of the specified index"""
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def is_in_universe(self):
        """Checks if an asset is part of the specified InvestmentUniverse"""
        raise NotImplementedError("This is an abstract method")

    def is_in_portfolio(self, portfolio: Portfolio) -> bool:
        """Checks if an asset is part of the specified Portfolio"""
        return bool(self in portfolio.nonzero_holdings)

    def get_weight_in_portfolio(self, portfolio: Portfolio) -> float:
        """Retrieves the weight of the Asset in the specified Portfolio"""
        weight_in_ptf = 0.0
        if self in portfolio.nonzero_holdings:
            weight_in_ptf = portfolio.nonzero_holdings[self]
        return weight_in_ptf


class Cash(Asset):
    """This class represents Cash."""

    def __init__(self, currency: Union[str, Currency] = Currency.EUR.value) -> None:
        super().__init__()
        self.currency = currency

    def __repr__(self) -> str:
        return str(self.currency)

    def __str__(self) -> str:
        return str(f"Cash in {self.currency}")

    def __hash__(self) -> int:
        return hash(str(self.currency))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cash):
            return NotImplemented
        return (self.currency) == (other.currency)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Cash):
            return NotImplemented
        return not self == other

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
