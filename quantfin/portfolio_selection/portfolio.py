"""
Created on Jan 3, 2022
@author: AC
"""

from optparse import Option
from typing import Dict, Optional, Set, Union

import numpy as np
import pandas as pd

from quantfin.market import assets


class Portfolio:
    """Class that represents a portfolio."""

    def __init__(
        self,
        name: Optional[str] = None,
        long_only: Optional[bool] = None,
        holdings: Optional[Dict[assets.IAsset, float]] = None,
        assets_returns: Optional[pd.DataFrame] = None,
    ):
        self.name = name
        self.long_only: bool = long_only or True
        self.holdings: Dict[assets.IAsset, float] = holdings or {
            assets.Cash(): assets.Cash.value
        }
        self.assets_returns = assets_returns
        if assets.Cash() not in self.holdings:
            # if cash is not specified in the holdings automatically compute it
            cash = assets.Cash(value=1.0 - np.abs(float(sum(self.holdings.values()))))
            if cash.value < 1e-4:
                cash.value = 0.0
            self.holdings[cash] = cash.value
        assert (
            1.0 - float(sum(self.holdings.values())) < 1e-4
        ), f"Holding weights should sum to one, not {float(sum(self.holdings.values()))}."

    @property
    def nonzero_holdings(self) -> Dict[assets.IAsset, float]:
        """Dictionary of portfolio holdings."""
        return {
            asset: weight
            for asset, weight in self.holdings.items()
            if self.holdings[asset] != 0.0
        }

    @property
    def instruments(self) -> Set[Union[assets.Cash, assets.IAsset]]:
        """Set of portfolio instruments."""
        return {
            asset
            for asset in self.holdings.keys()
            if (isinstance(asset, assets.IAsset) and self.holdings[asset] != 0.0)
        }

    @property
    def len_instruments(self) -> int:
        """Number of portfolio instruments."""
        return len(self.instruments)

    @property
    def cash(self) -> Dict[str, float]:
        """Cash in portfolio."""
        for asset in self.holdings.keys():
            if isinstance(asset, assets.Cash):
                cash = {asset.currency: asset.value}
            else:
                cash = {assets.Cash.currency: 0.0}
        return cash

    def get_returns(self) -> pd.DataFrame:
        """Not yet implemented."""
        if self.assets_returns:
            print("Asset's returns were already provided.")
            return self.assets_returns
        # else:
        # call the asset's get_returns method
        return pd.DataFrame()

    @property
    def variance(self):
        pass

    # @property
    # def expected_return(self) -> float:
    #     pass

    # @property
    # def sharpe_ratio(self) -> float:
    #     pass

    # @property
    # def mad(self) -> float:
    #     pass

    # @property
    # def maximum_drawdown(self) -> float:
    #     pass

    # @property
    # def serenity_ratio(self) -> float:
    #     pass

    # @property
    # def cdar(self) -> float:
    #     pass

    # @property
    # def cvar(self) -> float:
    #     pass

    # @property
    # def value_at_risk(self) -> float:
    #     pass

    # @property
    # def return_on_investment(self, num_holding_days: int) -> float:
    #     pass


class OptimalPortfolio(Portfolio):
    """Class that represents an optimal portfolio.

    Attributes
    ----------
    name : str
    long_only : bool, optional
        default is True
    holdings : dict, optional

    objective_function : str, optional

    start_holding_date pd.Timestamp, optional
    """

    def __init__(
        self,
        name: Optional[str] = None,
        long_only: Optional[bool] = None,
        holdings: Optional[Dict[assets.IAsset, float]] = None,
        assets_returns: Optional[pd.DataFrame] = None,
        objective_function: Optional[str] = None,
        start_holding_date: Optional[pd.Timestamp] = None,
    ):
        super().__init__(name, long_only, holdings, assets_returns)
        self.objective_function = objective_function
        self.start_holding_date = start_holding_date
