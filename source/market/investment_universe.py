"""
The investment_universe module provides a class to instantiate investment universes.
"""

from __future__ import annotations


class InvestmentUniverse:
    """
    This class represent an investment universe.
    """

    VALID_UNIVERSE_NAMES: set = {"SP500", "NASDAQ100"}

    def __init__(
        self,
        name: str,
    ) -> None:
        if name in InvestmentUniverse.VALID_UNIVERSE_NAMES:
            self.name = name
        else:
            raise ValueError(
                f"""Inappropriate universe name, 
                supported universes are: {InvestmentUniverse.VALID_UNIVERSE_NAMES}"""
            )
