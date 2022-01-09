"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations

from typing import List, Optional, Set

import pandas as pd

from quantfin.market.assets import Stock


class InvestmentUniverse:
    """
    This class represent an investment universe.
    """

    VALID_UNIVERSE_NAMES: set = {"SP500", "NASDAQ100"}

    def __init__(
        self,
        name: str,
        components: Optional[Set[Stock]] = None,
    ) -> None:
        if name in InvestmentUniverse.VALID_UNIVERSE_NAMES:
            self.name = name
        else:
            raise ValueError(
                f"""Inappropriate universe name, 
                supported universe names are: {InvestmentUniverse.VALID_UNIVERSE_NAMES}"""
            )
        self.components = components or self._get_components()

    def _get_components(
        self,
        source: str = "Wikipedia",
    ) -> Set[Stock]:
        VALID_SOURCES = {"Wikipedia"}  # pylint: disable=invalid-name
        if source not in VALID_SOURCES:
            raise ValueError(
                f"""The source is not valid, supported ones are: {VALID_SOURCES}"""
            )
        self.components = set()
        if self.name == "SP500":
            sp500_tickers: List = pd.read_html(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )[0]["Symbol"].tolist()
            for ticker in sp500_tickers:
                self.components.add(Stock(ticker=ticker))
        if self.name == "NASDAQ100":
            nasdaq100_tickers = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[
                3
            ]["Ticker"].tolist()
            for ticker in nasdaq100_tickers:
                self.components.add(Stock(ticker=ticker))
        return self.components
