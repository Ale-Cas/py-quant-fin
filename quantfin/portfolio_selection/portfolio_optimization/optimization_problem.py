"""Module to implement optimization problems."""

from typing import Any, Dict

import cvxopt as opt
import numpy as np
import pandas as pd

from quantfin.market import assets
from quantfin.portfolio_selection.portfolio import OptimalPortfolio
from quantfin.portfolio_selection.portfolio_optimization.objective_functions import (
    ObjectiveFunctions,
    CovarianceMatrix,
)


class OptimizationProblem:
    """Class that represents a generic optimization problem."""

    def __init__(
        self,
        obj_fun: ObjectiveFunctions,
    ) -> None:
        self.obj_fun = obj_fun

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        return OptimalPortfolio()


class QuadraticProgram(OptimizationProblem):
    """Class that represents a Quadratic Program."""

    def __init__(self) -> None:
        super().__init__(obj_fun=ObjectiveFunctions.VARIANCE)

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        if isinstance(self.obj_fun, CovarianceMatrix):
            covariance_df: pd.DataFrame = self.obj_fun()
            cov_matrix = opt.matrix(2 * covariance_df.values)
            n: int = len(covariance_df.columns)
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
            for ticker in covariance_df.columns:
                stocks.append(assets.Stock(ticker=ticker))
            opt_holdings: Dict[assets.IAsset, float] = dict(zip(stocks, weights))
            return OptimalPortfolio(
                name="Min Variance Portfolio",
                holdings=opt_holdings,
                objective_function=ObjectiveFunctions.VARIANCE.value,
            )
        else:
            raise NotImplementedError


class LinearProgram(OptimizationProblem):
    """Class that represents a linear programming problem."""

    def __init__(self) -> None:
        super().__init__(obj_fun=ObjectiveFunctions.MAD)

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        return OptimalPortfolio()
