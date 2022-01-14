"""Module to implement optimization problems."""

from quantfin.portfolio_selection.portfolio_optimization import objective_functions


class OptimizationProblem:
    """Class that represents an optimization problem."""

    def __init__(
        self,
        obj_fun: objective_functions.IObjectiveFunction,
    ) -> None:
        self.obj_fun = obj_fun
