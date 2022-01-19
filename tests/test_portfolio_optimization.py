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
    univ = InvestmentUniverse(name="NASDAQ 100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_variance = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.VARIANCE,
        constraints=[ConstraintType.NO_SHORTSELLING],
        regularization_weight=0.15,
    )
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio


def test_add_constraint() -> None:
    univ = InvestmentUniverse(name="NASDAQ 100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_variance = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.VARIANCE,
    )
    min_variance.add_constraint(constraint=ConstraintType.NO_SHORTSELLING)
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio


def test_mad() -> None:
    univ = InvestmentUniverse(name="NASDAQ 100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_mad = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.MAD,
        constraints=[ConstraintType.NO_SHORTSELLING],
        regularization_weight=0.15,
    )
    min_mad_portfolio = min_mad.solve()
    assert min_mad_portfolio


def test_cvar() -> None:
    univ = InvestmentUniverse(name="NASDAQ 100")
    rets = univ.get_prices(prices_column="Close").pct_change().dropna()
    min_cvar = OptimizationProblem(
        returns=rets,
        objective_type=ObjectiveType.CVAR,
        constraints=[ConstraintType.NO_SHORTSELLING],
        regularization_weight=0.1,
    )
    min_cvar_portfolio = min_cvar.solve()
    assert min_cvar_portfolio
