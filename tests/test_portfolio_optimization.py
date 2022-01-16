"""
Test portfolio optimization module.
"""
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio_optimization import (
    ObjectiveType,
    ConstraintType,
    OptimizationProblem,
)


def test_min_variance() -> None:
    univ = InvestmentUniverse(name="NASDAQ100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_variance = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.VARIANCE,
        constraints=[ConstraintType.NO_SHORTSELLING],
    )
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio


def test_add_constraint() -> None:
    univ = InvestmentUniverse(name="NASDAQ100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_variance = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.VARIANCE,
    )
    min_variance.add_constraint(constraint=ConstraintType.NO_SHORTSELLING)
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio
