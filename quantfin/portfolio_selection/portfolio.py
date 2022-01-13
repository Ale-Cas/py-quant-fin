"""
Created on Jan 3, 2022
@author: AC
"""

import numpy as np
from typing import Optional, Dict, Set, Union

from quantfin.market import assets


class Portfolio:
    """Class that represents a portfolio."""

    def __init__(
        self,
        holdings: Optional[Dict[assets.IAsset, float]] = None,
    ):
        self.holdings: Dict[assets.IAsset, float] = holdings or {
            assets.Cash(): assets.Cash.value
        }
        sum_of_weights = float(sum(self.holdings.values()))
        assert (
            np.abs(sum_of_weights - 1.0) < 1e-4
        ), f"Holding weights should sum to one, not {sum_of_weights}."

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
