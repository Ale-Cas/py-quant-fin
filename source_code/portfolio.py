"""
Created on Jan 3, 2022
@author: AC
"""
from typing import Dict, Union

from source_code.assets import Asset, Cash


class Portfolio:
    """
    This class represents Portfolios.
    """

    def __init__(
        self,
        name: str,  # = "default_portfolio_name",
        holdings: Dict[Union[Asset, Cash], float],
    ) -> None:
        self.name = name
        self.holdings = holdings or {Cash: 1.0}


class OptimalPortfolio(Portfolio):
    pass
