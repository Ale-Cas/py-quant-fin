"""Module to implement optimization problems."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import cvxopt as opt
import numpy as np
import pandas as pd

from quantfin.utils import ListEnum
from quantfin.market import assets
from quantfin.portfolio_selection.portfolio import OptimalPortfolio


class ObjectiveType(str, ListEnum):
    """List of objective functions."""

    VARIANCE = "Covariance Matrix"
    MAD = "Linearized Mean-Absolute-Deviation"
    CVAR = "Linearized Conditional-Value-at-Risk"


class ConstraintType(ListEnum):
    """List of constraints."""

    BUDGET = "BUDGET"
    NO_SHORTSELLING = "NO_SHORTSELLING"
    MAX_INSTRUMENT_WEIGHT = "MAX_INSTRUMENT_WEIGHT"


class OptimizationModel(ABC):
    """Class that represents an abstract optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType],
    ) -> None:
        self.returns = returns
        self.objective_type = objective_type
        self.constraints = constraints

    @property
    @abstractmethod
    def objective_function(self) -> Any:
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def solve(self) -> Any:
        """Solves the optimization problem."""
        raise NotImplementedError("Abstract method")


class MeanVariance(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType],
    ) -> None:
        super().__init__(returns, objective_type, constraints)

    @property
    def objective_function(self) -> np.array:
        return 2 * self.returns.cov().values

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        cov_matrix = opt.matrix(self.objective_function)
        n: int = len(self.returns.columns)
        # TODO: This should be in the constraint class or in another method:
        q = opt.matrix(0.0, (n, 1))
        # Inequality constraint G * x <= h
        G = -opt.matrix(np.eye(n))  # negative n x n identity matrix
        h = opt.matrix(0.0, (n, 1))
        # Equality constraint A * x = b
        A = opt.matrix(1.0, (1, n))
        b = opt.matrix(1.0)

        solution = opt.solvers.qp(P=cov_matrix, q=q, G=G, h=h, A=A, b=b)
        weights = np.array(solution["x"]).reshape(n)
        weights[weights < 1e-4] = 0.0
        stocks = []
        for ticker in self.returns.columns:
            stocks.append(assets.Stock(ticker=ticker))
        opt_holdings: Dict[assets.IAsset, float] = dict(zip(stocks, weights))
        return OptimalPortfolio(
            name="Min Variance Portfolio",
            holdings=opt_holdings,
            objective_function=ObjectiveType.VARIANCE.value,
        )


class MeanMAD(OptimizationModel):
    """Class that represents the Mean-MAD model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType],
    ) -> None:
        super().__init__(returns, objective_type, constraints)

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""

        return OptimalPortfolio()


class MeanCVaR(OptimizationModel):
    """Class that represents the Mean-CVaR model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType],
    ) -> None:
        super().__init__(returns, objective_type, constraints)

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        return OptimalPortfolio()


class OptimizationProblem:
    """Class that represents an abstract optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType],
    ) -> None:
        self.returns = returns
        self.objective_type = objective_type
        self.constraints = constraints

        if self.objective_type == ObjectiveType.VARIANCE:
            self.problem = MeanVariance(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
            )
        if self.objective_type == ObjectiveType.MAD:
            self.problem = MeanMAD(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
            )
        if self.objective_type == ObjectiveType.CVAR:
            self.problem = MeanCVaR(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
            )

    @property
    def objective_function(self) -> np.array:
        return self.problem.objective_function

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        return self.problem.solve()
