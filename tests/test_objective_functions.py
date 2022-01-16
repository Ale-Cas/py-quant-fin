from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio_optimization.objective_functions import (
    CovarianceMatrix,
    LinearMAD,
)


def test_covariance_matrix() -> None:
    univ = InvestmentUniverse(name="NASDAQ100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    covariance = CovarianceMatrix(returns=rets)
    assert covariance


def test_linear_mad() -> None:
    univ = InvestmentUniverse(name="NASDAQ100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    mad = LinearMAD(returns=rets)
    assert mad
