"""Module to implement optimization problems."""

from typing import Any, Dict
import numpy as np
import pandas as pd
import cvxopt as opt

from quantfin.market import assets
from quantfin.portfolio_selection.portfolio_optimization import objective_functions
from quantfin.portfolio_selection import portfolio


class OptimizationProblem:
    """Class that represents a generic optimization problem."""

    def __init__(
        self,
        obj_fun: objective_functions.ObjectiveFunctionType,
    ) -> None:
        self.obj_fun = obj_fun

    def solve(self) -> portfolio.OptimalPortfolio:
        """Solves the optimization problem."""
        return portfolio.OptimalPortfolio()


class QuadraticProgram(OptimizationProblem):
    """Class that represents a Quadratic Program."""

    def __init__(self, obj_fun: objective_functions.ObjectiveFunctionType) -> None:
        super().__init__(obj_fun)

    def solve(self) -> Any:
        """Solves the optimization problem."""
        if isinstance(self.obj_fun, objective_functions.CovarianceMatrix):
            covariance_df: pd.DataFrame = self.obj_fun()
            cov_matrix = opt.matrix(covariance_df.values)
            n: int = len(covariance_df.columns)
            # TODO: This should be in the constraint class or in another method:
            q = opt.matrix(0.0, (n, 1))
            G = -opt.matrix(np.eye(n))  # negative n x n identity matrix
            h = opt.matrix(0.0, (n, 1))
            A = opt.matrix(1.0, (1, n))
            b = opt.matrix(1.0)

            solution = opt.solvers.qp(P=cov_matrix, q=q, G=G, h=h, A=A, b=b)
            weights = np.array(solution["x"]).reshape(n)
            weights[weights < 1e-4] = 0.0
            stocks = []
            for ticker in covariance_df.columns:
                stocks.append(assets.Stock(ticker=ticker))
            opt_holdings: Dict[assets.IAsset, float] = dict(zip(stocks, weights))
            return portfolio.OptimalPortfolio(
                name=objective_functions.ObjectiveFunctionType.MIN_VARIANCE,
                holdings=opt_holdings,
            )
        else:
            raise NotImplementedError
