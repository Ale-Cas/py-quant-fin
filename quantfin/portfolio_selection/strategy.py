"""
Strategy design pattern implementation for different portfolio selection models.

Interface -> Model: 
    PortfolioSelectionModel:
    - OptimizationModel
    - RiskParityModel

Context -> Problem:
    PortfolioSelectionProblem
    - OptimizationProblem
    - RiskParityProblem

"""

from abc import ABC, abstractmethod
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio import OptimalPortfolio
from quantfin.utils import ListEnum


class PortfolioStrategies(str, ListEnum):
    PTF_OPT = "Portfolio Optimization"
    RISK_PARITY = "Risk Parity"


class PortfolioSelectionModel(ABC):
    """Strategy interface."""

    @abstractmethod
    def compute_optimal_portfolio(
        self,
        investment_universe: InvestmentUniverse,
        cash_pct: float = 0.0,
    ) -> OptimalPortfolio:
        pass


class PortfolioSelectionProblem:
    """Context class to define the PortfolioSelectionModel of interest."""

    def __init__(
        self,
        portfolio_selection_model: PortfolioSelectionModel,
        investment_universe: InvestmentUniverse,
        cash_percentage: float = 0.0,
    ) -> None:
        self.portfolio_selection_model = portfolio_selection_model
        self.investment_universe = investment_universe
        self.cash_percentage = cash_percentage

    def solve(self) -> OptimalPortfolio:
        """Solve the specified Portfolio Selection Problem and return an OptimalPortfolio object."""
        return self.portfolio_selection_model.compute_optimal_portfolio(
            investment_universe=self.investment_universe,
            cash_pct=self.cash_percentage,
        )
