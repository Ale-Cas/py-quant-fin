"""
Created on Jan 3, 2022
@author: AC
"""

from typing import Dict, Optional, Set, Union

import numpy as np

from quantfin.market import assets


class Portfolio:
    """Class that represents a portfolio."""

    def __init__(
        self,
        name: Optional[str] = None,
        long_only: Optional[bool] = None,
        holdings: Optional[Dict[assets.IAsset, float]] = None,
    ):
        self.name = name
        self.long_only: bool = long_only or True
        self.holdings: Dict[assets.IAsset, float] = holdings or {
            assets.Cash(): assets.Cash.value
        }
        if assets.Cash() not in self.holdings:
            # if cash is not specified in the holdings automatically compute it
            cash = assets.Cash(value=np.abs(1.0 - float(sum(self.holdings.values()))))
            self.holdings[cash] = cash.value
        assert (
            float(sum(self.holdings.values())) == 1.0
        ), f"Holding weights should sum to one, not {float(sum(self.holdings.values()))}."

    @property
    def cash(self) -> float:
        raise NotImplementedError

    @property
    def instruments(self) -> Set[Union[assets.Cash, assets.IAsset]]:
        """List of portfolio instruments."""
        return {
            asset
            for asset in self.holdings.keys()
            if (isinstance(asset, assets.IAsset) and self.holdings[asset] != 0.0)
        }

    @property
    def len_instruments(self) -> int:
        """Number of portfolio instruments."""
        return len(self.instruments)


class OptimalPortfolio(Portfolio):
    pass
