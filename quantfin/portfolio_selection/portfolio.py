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
        holdings: Optional[
            Union[Dict[assets.Cash, float], Dict[assets.IAsset, float]]
        ] = None,
    ):
        self.holdings: Union[
            Dict[assets.Cash, float], Dict[assets.IAsset, float]
        ] = holdings or {assets.Cash: assets.Cash.value}
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
            x
            for x in self.holdings.keys()
            if (x != ("$" + self.base_currency) and self.holdings[x] != 0.0)
        }

    @property
    def len_instruments(self) -> Set[Union[assets.Cash, assets.IAsset]]:
        """Number of portfolio instruments."""
        return len(self.instruments)


class OptimalPortfolio(Portfolio):
    pass
