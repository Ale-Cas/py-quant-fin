"""Module to implement optimization problems."""
from typing import Dict, List, Optional, Union

import cvxopt as opt
import numpy as np
import pandas as pd

from quantfin.market import assets
from quantfin.portfolio_selection.portfolio import OptimalPortfolio
from quantfin.utils import ListEnum


class ObjectiveType(str, ListEnum):
    """List of objective functions."""

    VARIANCE = "Variance"
    MAD = "Mean-Absolute-Deviation"
    CVAR = "Conditional-Value-at-Risk"


class ConstraintType(ListEnum):
    """List of constraints."""

    NO_SHORTSELLING = "No short-selling"
    CASH_PCT = "Minimum cash percentage"


class OptimizationModel:
    """Class that represents an abstract optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: Optional[float] = None,
        cash_pct: Optional[float] = None,
    ) -> None:
        self.returns = returns
        self.objective_type = objective_type
        self.constraints = constraints
        self.regularization_weight = regularization_weight or 0.05
        if ConstraintType.CASH_PCT in self.constraints:
            # if the constraint is selected
            # but the percentage is not provided
            # defaults to 2% of portfolio in cash
            self.cash_pct = cash_pct or 0.02
        else:
            self.cash_pct = cash_pct

    def add_constraint(self, constraint: ConstraintType) -> None:
        if isinstance(constraint, ConstraintType):
            self.constraints.append(constraint)
        else:
            raise ValueError(
                f"""The constraint type is not valid, 
                    supported constraints are: {",".join(ConstraintType.list())}"""
            )

    @property
    def num_assets(self) -> int:
        return len(self.returns.columns)

    @property
    def num_obs(self) -> int:
        return len(self.returns.index)

    @property
    def objective_function(self) -> Dict[str, Union[np.array, float]]:
        if self.regularization_weight:
            {
                "Quadratic": np.eye(self.num_assets) * self.regularization_weight,
                "Linear": np.zeros(shape=(self.num_assets, 1)),
            }
        else:
            {
                "Quadratic": np.zeros(shape=(self.num_assets, self.num_assets)),
                "Linear": np.zeros(shape=(self.num_assets, 1)),
            }

    def get_constraints(self) -> Dict[str, Union[np.array, float]]:
        """Computes the constraints and returns them in a dictionary."""
        constraints_dict = {}
        A_budget = np.hstack(
            (
                np.ones(self.num_assets),
                np.zeros(len(self.objective_function["Linear"]) - self.num_assets),
            )
        )
        constraints_dict["A_budget"] = np.reshape(A_budget, (1, len(A_budget)))
        if ConstraintType.CASH_PCT in self.constraints:
            constraints_dict["b_budget"] = 1.0 - self.cash_pct
        else:
            constraints_dict["b_budget"] = 1.0
        return constraints_dict

    def solve(self) -> OptimalPortfolio:
        """Solves the following optimization problem.

        minimize:
                    (1/2)*x'*P*x + q'*x
        subject to:
                    G*x <= h
                    A*x = b.
        """
        objectives_matrices = {
            name: opt.matrix(objective)
            for name, objective in self.objective_function.items()
        }
        constraints_matrices = {
            name: opt.matrix(constraint)
            for name, constraint in self.get_constraints().items()
        }
        if ConstraintType.NO_SHORTSELLING in self.constraints:
            solution = opt.solvers.qp(
                P=objectives_matrices["Quadratic"],
                q=objectives_matrices["Linear"],
                G=constraints_matrices["G_inequality"],
                h=constraints_matrices["h_inequality"],
                A=constraints_matrices["A_budget"],
                b=constraints_matrices["b_budget"],
            )
        else:
            solution = opt.solvers.qp(
                P=objectives_matrices["Quadratic"],
                q=objectives_matrices["Linear"],
                A=constraints_matrices["A_budget"],
                b=constraints_matrices["b_budget"],
            )
        assert (
            solution["status"] == "optimal"
        ), "The status of the solution is not optimal!"
        weights = np.array(solution["x"]).reshape(np.array(solution["x"]).size)[
            0 : self.num_assets
        ]
        weights[weights < 1e-4] = 0.0
        stocks = []
        for ticker in self.returns.columns:
            stocks.append(assets.Stock(ticker=ticker))
        opt_holdings: Dict[assets.IAsset, float] = dict(zip(stocks, weights))
        return OptimalPortfolio(
            name=f"Min {self.objective_type.value} Portfolio",
            holdings=opt_holdings,
            objective_function=ObjectiveType.VARIANCE.value,
        )


class MeanVariance(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: Optional[float] = None,
        cash_pct: Optional[float] = None,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )

    def get_constraints(self) -> Dict[str, Union[np.array, float]]:
        """Computes the constraints and returns them in a dictionary."""
        constraints_dict = OptimizationModel.get_constraints()
        # The Mean-Variance model has a different definition of the A_budget matrix
        constraints_dict["A_budget"] = np.ones(shape=(1, self.num_assets))

        if ConstraintType.NO_SHORTSELLING in self.constraints:
            # Inequality constraint G * x <= h
            constraints_dict["G_inequality"] = -np.eye(
                self.num_assets
            )  # negative n x n identity matrix
            constraints_dict["h_inequality"] = np.zeros(shape=(self.num_assets, 1))

        # TODO: #10 Add other constraints
        return constraints_dict

    @property
    def objective_function(self) -> Dict[str, Union[np.array, float]]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        Quadratic
            Quadratic part of the objective function
        Linear
            Linear part (already transposed)
        """
        return {
            "Quadratic": 2 * self.returns.cov().values,
            "Linear": np.zeros(shape=(self.num_assets, 1)),
        }


class MeanMAD(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
    ) -> None:
        super().__init__(returns, objective_type, constraints)

    def get_constraints(self) -> Dict[str, Union[np.array, float]]:
        """Get the constraints and computes them."""
        constraints_dict = OptimizationModel.get_constraints()
        # FIXME: #11 Implement MAD constraints

        # TODO: #10 Add other constraints
        return constraints_dict

    @property
    def objective_function(self) -> Dict[str, Union[np.array, float]]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        q
            Linear objective function
        """
        objective_dict = OptimizationModel.objective_function
        linear_mad = np.hstack(
            (np.zeros(self.num_assets), np.ones(self.num_obs) / self.num_obs)
        )
        objective_dict["Linear"] = linear_mad
        return objective_dict


class MeanCVaR(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    # FIXME: #12 Implement CVaR model

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: Optional[float] = None,
        cash_pct: Optional[float] = None,
        confidence_level: float = 0.05,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )
        self.confidence_level = confidence_level

    def get_constraints(self) -> Dict[str, Union[np.array, float]]:
        """Get the constraints and computes them."""
        constraints_dict = OptimizationModel.get_constraints()

        # TODO: #10 Add other constraints
        return constraints_dict


class OptimizationProblem(OptimizationModel):
    """Class that selects the optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: Optional[float] = None,
        cash_pct: Optional[float] = None,
        confidence_level: float = 0.05,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )

        if self.objective_type == ObjectiveType.VARIANCE:
            self.model = MeanVariance(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                regularization_weight=self.regularization_weight,
                cash_pct=self.cash_pct,
            )
        if self.objective_type == ObjectiveType.MAD:
            self.model = MeanMAD(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                regularization_weight=self.regularization_weight,
                cash_pct=self.cash_pct,
            )
        if self.objective_type == ObjectiveType.CVAR:
            self.confidence_level = confidence_level or 0.05
            self.model = MeanCVaR(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                regularization_weight=self.regularization_weight,
                cash_pct=self.cash_pct,
            )

    def get_constraints(self) -> Dict[str, np.array]:
        """Get the constraints and computes them."""
        return self.model.get_constraints()

    @property
    def objective_function(self) -> np.array:
        return self.model.objective_function

    def solve(self) -> OptimalPortfolio:
        """Solves the optimization problem."""
        return self.model.solve()
