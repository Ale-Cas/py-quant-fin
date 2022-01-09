"""
The market_data module provides classes for downloading prices from supported data_providers.
"""

from __future__ import annotations
from source.market.investment_universe import InvestmentUniverse
from source.market.data_sources import DataProviders


class MarketData:
    """
    This class is a wrapper to get market data
    for all the specified instruments inside an investment universe,
    from the specified data provider.
    """

    def __init__(
        self,
        investment_universe: InvestmentUniverse,
        data_provider: DataProviders,
    ) -> None:
        """
        Parameters
        ----------
        investment_universe: InvestmentUniverse
            The investment universe.
        data_provider: DataProviders
            The data provider to take data.
        """

        self.data_provider = data_provider
        self.investment_universe = investment_universe
