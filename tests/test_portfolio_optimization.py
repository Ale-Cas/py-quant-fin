"""
Test portfolio optimization module.
"""
import pytest

from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio_optimization import (
    MeanCVaR,
    MeanMAD,
    MeanVariance,
    Constraint,
    OptimizationProblem,
)
from quantfin.portfolio_selection.risk_parity import HierarchicalRiskParity


@pytest.fixture(scope="module")
def nasdaq_inv_univ() -> InvestmentUniverse:
    nasdaq = InvestmentUniverse(reference_index="NASDAQ 100")
    nasdaq.returns = nasdaq.get_returns()
    return nasdaq


@pytest.fixture(scope="module")
def custom_inv_univ() -> InvestmentUniverse:
    cst_tickers = ["AAPL", "GOOG", "IBM", "MSFT", "TSLA"]
    univ = InvestmentUniverse(tickers=cst_tickers)
    start_date = "2019-01-20"
    end_date = "2021-11-20"
    univ.get_returns(price_type="Close", start=start_date, end=end_date)
    return univ


def test_min_variance_with_custom_tickers(custom_inv_univ: InvestmentUniverse) -> None:
    min_variance = OptimizationProblem(
        optimization_model=MeanVariance(
            constraints={Constraint.NO_SHORTSELLING},
        ),
        investment_universe=custom_inv_univ,
    )
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio
    assert min(min_variance_portfolio.holdings.values()) == 0


def test_min_variance(nasdaq_inv_univ: InvestmentUniverse) -> None:
    min_variance = OptimizationProblem(
        optimization_model=MeanVariance(
            constraints={Constraint.NO_SHORTSELLING},
        ),
        investment_universe=nasdaq_inv_univ,
    )
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio
    assert min(min_variance_portfolio.holdings.values()) == 0


def test_add_constraint(custom_inv_univ: InvestmentUniverse) -> None:
    model = MeanVariance()
    model.add_constraint(Constraint.NO_SHORTSELLING)
    min_variance = OptimizationProblem(
        optimization_model=model,
        investment_universe=custom_inv_univ,
    )
    min_variance_portfolio = min_variance.solve()
    assert min_variance_portfolio
    assert min(min_variance_portfolio.holdings.values()) == 0


def test_mad_with_custom_tickers(custom_inv_univ: InvestmentUniverse) -> None:
    min_mad = OptimizationProblem(
        optimization_model=MeanMAD(
            constraints={Constraint.NO_SHORTSELLING},
        ),
        investment_universe=custom_inv_univ,
    )
    min_mad_portfolio = min_mad.solve()
    assert min_mad_portfolio
    assert min(min_mad_portfolio.holdings.values()) == 0


def test_mad(nasdaq_inv_univ: InvestmentUniverse) -> None:
    min_mad = OptimizationProblem(
        optimization_model=MeanMAD(
            constraints={Constraint.NO_SHORTSELLING},
        ),
        investment_universe=nasdaq_inv_univ,
    )
    min_mad_portfolio = min_mad.solve()
    assert min_mad_portfolio
    assert min(min_mad_portfolio.holdings.values()) == 0


def test_cvar_with_custom_tickers(custom_inv_univ: InvestmentUniverse) -> None:
    min_cvar = OptimizationProblem(
        optimization_model=MeanCVaR(
            constraints={Constraint.NO_SHORTSELLING},
        ),
        investment_universe=custom_inv_univ,
    )
    min_cvar_portfolio = min_cvar.solve()
    assert min_cvar_portfolio
    assert min(min_cvar_portfolio.holdings.values()) == 0


def test_cvar_nasdaq(nasdaq_inv_univ: InvestmentUniverse) -> None:
    min_cvar = OptimizationProblem(
        optimization_model=MeanCVaR(
            constraints={Constraint.NO_SHORTSELLING},
        ),
        investment_universe=nasdaq_inv_univ,
    )
    min_cvar_portfolio = min_cvar.solve()
    assert min_cvar_portfolio
    assert min(min_cvar_portfolio.holdings.values()) == 0


def test_hrp(nasdaq_inv_univ: InvestmentUniverse) -> None:
    nasdaq = InvestmentUniverse(reference_index="NASDAQ 100")
    nasdaq.returns = nasdaq.get_returns()
    hrp = HierarchicalRiskParity(investment_universe=nasdaq)
    hrp_ptf = hrp.compute_optimal_portfolio()
    assert hrp_ptf
    assert min(hrp_ptf.holdings.values()) == 0
