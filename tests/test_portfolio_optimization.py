"""
Test portfolio optimization module.
"""
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio_optimization.objective_functions import (
    CovarianceMatrix,
)
from quantfin.portfolio_selection.portfolio_optimization.optimization_problem import (
    QuadraticProgram,
)


def test_min_variance() -> None:
    univ = InvestmentUniverse(name="NASDAQ100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    objective = CovarianceMatrix(returns=rets)
    qp = QuadraticProgram(obj_fun=objective)
    portfolio = qp.solve()
    assert portfolio
