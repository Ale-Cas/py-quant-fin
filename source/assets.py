"""Abstraction layer for Assets."""
from __future__ import annotations
import dataclasses
from typing import Optional

import pandas as pd

from source.portfolio import Portfolio


@dataclasses.dataclass
class Cash:
    """This class represents Cash."""

    currency: str = "EUR"


class Asset:
    """
    This class represent a single asset.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        asset_class: Optional[str] = None,
        data_provider: Optional[str] = "Yahoo Finance",
        prices: pd.DataFrame = pd.DataFrame(),
    ) -> None:
        """
        Initialize the Asset
        """
        self.name = name
        self.ticker = ticker
        self.isin = isin
        self.exchange = exchange
        self.asset_class = asset_class
        self.data_provider = data_provider
        self.prices = prices

    def weight_in_ptf(
        self,
        portfolio: Portfolio,
    ) -> Portfolio:
        """Retrieves the weight of the Asset in the specified Portfolio"""
        return portfolio


class Stock(Asset):
    """
    This class represent a single stock.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,
        exchange: Optional[str] = None,
        data_provider: Optional[str] = "Alpaca",
    ) -> None:
        """
        Initialize the Stock
        """
        super().__init__(
            name,
            ticker,
            isin,
            exchange,
            asset_class="equity",
            data_provider=data_provider,
        )
