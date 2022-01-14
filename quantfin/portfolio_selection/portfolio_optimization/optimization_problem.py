"""Module to implement optimization problems."""

# from cvxopt import matrix, solvers

from quantfin.portfolio_selection.portfolio_optimization import objective_functions
from quantfin.portfolio_selection import portfolio


class OptimizationProblem:
    """Class that represents an optimization problem."""

    def __init__(
        self,
        obj_fun: objective_functions.ObjectiveFunctionType,
    ) -> None:
        self.obj_fun = obj_fun

    def solve(self) -> portfolio.OptimalPortfolio:
        """Solves the optimization problem."""
        return portfolio.OptimalPortfolio()
