"""
Test portfolio optimization module.
"""
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio_optimization.optimization_problem import (
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
        constraints=[ConstraintType.BUDGET],
    )
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio
