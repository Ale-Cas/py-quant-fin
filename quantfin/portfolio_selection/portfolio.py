"""
Created on Jan 3, 2022
@author: AC
"""

from typing import Dict, Optional, Set, Union

import numpy as np
import pandas as pd

from quantfin.market import assets


class Portfolio:
    """Class that represents a portfolio."""

    def __init__(
        self,
        name: Optional[str] = None,
        long_only: bool = True,
        currency: assets.Currency = assets.Currency.EUR,
        holdings: Optional[Dict[assets.Asset, float]] = None,
        assets_returns: pd.DataFrame = pd.DataFrame(),
    ):
        self.name = name
        self.long_only = long_only
        self.currency = currency
        self.holdings = holdings or {assets.Cash(currency=self.currency): 1.0}
        self.assets_returns = assets_returns
        cash = assets.Cash(currency=self.currency)
        if cash not in self.holdings:
            # if cash is not specified in the holdings automatically compute it
            self.holdings[cash] = 1.0 - np.abs(float(sum(self.holdings.values())))
            if self.holdings[cash] < 1e-4:
                self.holdings[cash] = 0.0
        assert (
            float(sum(self.holdings.values())) - 1.0 < 1e-4
        ), f"Holding weights should sum to one, not {float(sum(self.holdings.values()))}."

    @property
    def nonzero_holdings(self) -> Dict[assets.Asset, float]:
        """Dictionary of portfolio holdings."""
        return {
            asset: weight
            for asset, weight in self.holdings.items()
            if self.holdings[asset] != 0.0
        }

    @property
    def instruments(self) -> Set[Union[assets.Cash, assets.Asset]]:
        """Set of portfolio instruments."""
        return {
            asset
            for asset in self.holdings.keys()
            if (isinstance(asset, assets.Asset) and self.holdings[asset] != 0.0)
        }

    @property
    def len_instruments(self) -> int:
        """Number of portfolio instruments."""
        return len(self.instruments)

    @property
    def cash(self) -> Dict[assets.Cash, float]:
        """Cash in portfolio."""
        for asset in self.holdings.keys():
            if isinstance(asset, assets.Cash):
                cash = {asset: self.holdings[asset]}
            else:
                cash = {assets.Cash(): 0.0}
        return cash

    def get_returns(self) -> pd.DataFrame:
        """Not yet implemented."""
        if not self.assets_returns.empty:
            print("Asset's returns were already provided.")
        else:
            for asset in self.holdings.keys():
                self.assets_returns[asset] = asset.prices
        return self.assets_returns

    @property
    def variance(self):
        # FIXME: Like this is very slow and inefficient -> O(n^2)
        # TODO: at least cache the property
        ptf_var = 0
        for col in self.assets_returns.cov().columns:
            for row in self.assets_returns.cov().index:
                ptf_var += (
                    self.holdings[col]
                    * self.assets_returns.cov()[col][row]
                    * self.holdings[row]
                )
        return ptf_var

    @property
    def expected_return(self) -> float:
        assert not self.assets_returns.empty, "Asset returns must be provided."
        exp_ret = 0
        for asset, weight in self.holdings.items():
            if isinstance(asset, assets.Cash):
                continue
            else:
                exp_ret += weight * self.assets_returns.mean()[asset.ticker]
        return exp_ret

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
        long_only: bool = True,
        currency: assets.Currency = assets.Currency.EUR,
        holdings: Optional[Dict[assets.Asset, float]] = None,
        assets_returns: Optional[pd.DataFrame] = None,
        objective_function: Optional[str] = None,
        start_holding_date: Optional[pd.Timestamp] = None,
    ):
        super().__init__(name, long_only, currency, holdings, assets_returns)
        self.objective_function = objective_function
        self.start_holding_date = start_holding_date
