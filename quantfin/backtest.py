"""
This module implements a framework to backtest strategies.
"""
from typing import List, Optional, Set
import pandas as pd

from quantfin.utils import ListEnum
from quantfin.portfolio_selection.strategies import PortfolioStrategies
from quantfin.market.investment_universe import InvestmentUniverse, MarketIndex
from quantfin.portfolio_selection.portfolio_optimization import (
    ObjectiveType,
    ConstraintType,
    OptimizationProblem,
)


class RebalanceFrequence(ListEnum):
    """List of available rebalance frequencies."""

    W = "Weekly"
    M = "Monthly"


class Backtest:
    """Class to perform a backtest."""

    def __init__(
        self,
        strategy: PortfolioStrategies = PortfolioStrategies.PTF_OPT,
        investment_universe: InvestmentUniverse = InvestmentUniverse(
            name="NASDAQ 100", reference_index=MarketIndex.NASDAQ100.value
        ),
        objective_function: ObjectiveType = ObjectiveType.VARIANCE,
        constraints: Set[ConstraintType] = {ConstraintType.NO_SHORTSELLING},
        rebalance_freq: RebalanceFrequence = RebalanceFrequence.M,
        rebalance_dates: Optional[List[pd.Timestamp]] = None,
    ) -> None:
        self.strategy = strategy
        self.investment_universe = investment_universe
        self.objective_function = objective_function
        self.constraints = constraints
        self.rebalance_freq = rebalance_freq
        self.rebalance_dates = rebalance_dates

    # def run(self) -> None:
    #     """Run the backtest."""
    #     pass
