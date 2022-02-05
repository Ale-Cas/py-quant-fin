"""
Test backtest module.
"""

from quantfin.portfolio_selection.strategies import PortfolioStrategies
from quantfin.portfolio_selection.portfolio_optimization import (
    OptimizationProblem,
    ObjectiveType,
    ConstraintType,
)
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.backtest import Backtest


def test_init() -> None:
    univ = InvestmentUniverse(reference_index="NASDAQ 100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_variance = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.VARIANCE,
        constraints=[ConstraintType.NO_SHORTSELLING],
        regularization_weight=0.15,
    )
    bt = Backtest(optimization_problem=min_variance)
    assert isinstance(bt, Backtest)
