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

    # def get_returns(self) -> pd.DataFrame:
    #     """Not yet implemented."""
    #     if not self.assets_returns.empty:
    #         print("Asset's returns were already provided.")
    #     else:
    #         for asset in self.holdings.keys():
    #             self.assets_returns[asset] = asset.prices
    #     return self.assets_returns

    @property
    def returns(self) -> pd.Series:
        assert not self.assets_returns.empty, "Asset returns must be provided."
        temp_holdings = pd.Series(self.holdings).drop(labels=self.currency)
        return temp_holdings @ self.assets_returns.T

    @property
    def variance(self) -> float:
        assert not self.assets_returns.empty, "Asset returns must be provided."
        temp_holdings = pd.Series(self.holdings).drop(labels=self.currency)
        return temp_holdings @ self.assets_returns.cov() @ temp_holdings.T

    @property
    def expected_return(self) -> float:
        assert not self.assets_returns.empty, "Asset returns must be provided."
        temp_holdings = pd.Series(self.holdings).drop(labels=self.currency)
        return (temp_holdings @ self.assets_returns.mean()).sum()

    @property
    def sharpe_ratio(self) -> float:
        return self.expected_return / np.sqrt(self.variance)

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

    def return_on_investment(
        self,
        start_date: Union[pd.Timestamp, str] = str(
            pd.Timestamp.today().date() - pd.DateOffset(years=1)
        ),
        holding_period: Union[pd.Timedelta, pd.DateOffset] = pd.DateOffset(years=1),
    ) -> float:
        """Compute Return on Investment (ROI).

        Parameters
        ----------
        start_date: pd.Timestamp or string
            Note: start_date is included
            default = 1 year ago
        holding_period: pd.Timedelta or pd.DateOffset
            default = 1 year
        """
        if isinstance(start_date, str):
            start_date = pd.Timestamp(start_date)
        else:
            raise ValueError("Provide a start_date in a string or pd.Timestamp format!")

        roi_temp = self.returns[
            lambda x: (x.index >= str(start_date.date()))
            & (x.index <= str((start_date + holding_period).date()))
        ]
        assert not roi_temp.empty, (
            "The specified start_date is not in the portfolio returns, "
            + "or the holding_period is too large,"
        )
        return roi_temp.sum()


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
