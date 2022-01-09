"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations
from typing import Optional, List

from quantfin.market.assets import Asset


class InvestmentUniverse:
    """
    This class represent an investment universe.
    """

    VALID_UNIVERSE_NAMES: set = {"SP500", "NASDAQ100"}

    def __init__(
        self,
        name: str,
        components: Optional[List[Asset]] = None,
    ) -> None:
        if name in InvestmentUniverse.VALID_UNIVERSE_NAMES:
            self.name = name
        else:
            raise ValueError(
                f"""Inappropriate universe name, 
                supported universes are: {InvestmentUniverse.VALID_UNIVERSE_NAMES}"""
            )
        self.components = components

    def _get_components_tickers(
        self,
        source: str = "Wikipedia",
    ) -> Optional[List[Asset]]:
        VALID_SOURCES = {"Wikipedia"}  # pylint: disable=invalid-name
        if source not in VALID_SOURCES:
            raise ValueError(
                f"""The source is not valid, supported ones are: {VALID_SOURCES}"""
            )

        return self.components
