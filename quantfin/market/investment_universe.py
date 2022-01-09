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
                supported universes are: {InvestmentUniverse.VALID_UNIVERSE_NAMES}"""
            )
        self.components = components or set()

    def _get_components_tickers(
        self,
        source: str = "Wikipedia",
    ) -> Optional[Set[Stock]]:
        VALID_SOURCES = {"Wikipedia"}  # pylint: disable=invalid-name
        if source not in VALID_SOURCES:
            raise ValueError(
                f"""The source is not valid, supported ones are: {VALID_SOURCES}"""
            )
        if self.name == "SP500":
            sp500_components: List = pd.read_html(
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )[0]["Symbol"].tolist()
            for ticker in sp500_components:
                self.components.add(Stock(ticker=ticker))
        return self.components
