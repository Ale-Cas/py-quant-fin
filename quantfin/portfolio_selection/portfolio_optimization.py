"""Module to implement optimization problems."""
from turtle import shape
from typing import Dict, List, Set

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


class OptimizationModel:
    """Class that represents an abstract optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: Set[ConstraintType] = [],
        regularization_weight: float = 0.05,
        cash_pct: float = 0.0,
    ) -> None:
        self.returns = returns
        self.objective_type = objective_type
        self.constraints = constraints
        self.regularization_weight = regularization_weight
        self.cash_pct = cash_pct

    def add_constraint(self, constraint: ConstraintType) -> None:
        if isinstance(constraint, ConstraintType):
            self.constraints.add(constraint)
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
    def objective_function(self) -> Dict[str, np.ndarray]:
        objective_dict = {}
        objective_dict["Linear"] = np.zeros(self.num_assets)
        objective_dict["Quadratic"] = (
            np.eye(len(objective_dict["Linear"])) * self.regularization_weight
        )
        return objective_dict

    def get_constraints(self) -> Dict[str, np.ndarray]:
        """Computes the constraints and returns them in a dictionary."""
        constraints_dict = {}
        A_budget = np.hstack(
            (
                np.ones(self.num_assets),
                np.zeros(len(self.objective_function["Linear"]) - self.num_assets),
            )
        )
        constraints_dict["A_budget"] = np.reshape(A_budget, (1, len(A_budget)))
        constraints_dict["b_budget"] = (1.0 - self.cash_pct) * np.ones(
            1
        )  # to make mypy happy
        if ConstraintType.NO_SHORTSELLING in self.constraints:

            G_no_short = np.concatenate(
                (
                    -np.eye(self.num_assets),
                    np.zeros(
                        (
                            self.num_assets,
                            len(self.objective_function["Linear"]) - self.num_assets,
                        )
                    ),
                ),
                axis=1,
            )
            h_no_short = np.zeros(self.num_assets)
            constraints_dict["G_inequality"] = G_no_short
            constraints_dict["h_inequality"] = h_no_short
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
        solution = opt.solvers.qp(
            P=objectives_matrices["Quadratic"],
            q=objectives_matrices["Linear"],
            G=constraints_matrices["G_inequality"],
            h=constraints_matrices["h_inequality"],
            A=constraints_matrices["A_budget"],
            b=constraints_matrices["b_budget"],
        )
        if (
            ConstraintType.NO_SHORTSELLING not in self.constraints
            and self.objective_type == ObjectiveType.VARIANCE
        ):
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
        stocks = []
        for ticker in self.returns.columns:
            stocks.append(assets.Stock(ticker=ticker))
        opt_holdings: Dict[assets.Asset, float] = dict(zip(stocks, weights))

        for asset, weight in opt_holdings.items():
            if weight > 0 and weight < 1e-4:
                opt_holdings[asset] = 0.0
        return OptimalPortfolio(
            name=f"Min {self.objective_type.value} Portfolio",
            holdings=opt_holdings,
            assets_returns=self.returns,
            objective_function=ObjectiveType.VARIANCE.value,
        )


class MeanVariance(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: float = 0.05,
        cash_pct: float = 0,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )

    @property
    def objective_function(self) -> Dict[str, np.ndarray]:
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

    def get_constraints(self) -> Dict[str, np.ndarray]:
        """Computes the constraints and returns them in a dictionary."""
        constraints_dict = super().get_constraints()
        # The Mean-Variance model has a different definition of the A_budget matrix
        constraints_dict["A_budget"] = np.ones(shape=(1, self.num_assets))

        if ConstraintType.NO_SHORTSELLING in self.constraints:
            # Inequality constraint G * x <= h
            constraints_dict["G_inequality"] = -np.eye(self.num_assets)

        # TODO: #10 Add other constraints
        return constraints_dict


class MeanMAD(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: float = 0.05,
        cash_pct: float = 0,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )

    @property
    def objective_function(self) -> Dict[str, np.ndarray]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        Linear
            Linear objective function
        Quadratic
            Quadratoc objective function
        """
        objective_dict = super().objective_function
        linear_mad = np.hstack(
            (np.zeros(self.num_assets), np.ones(self.num_obs) / self.num_obs)
        )
        objective_dict["Linear"] = linear_mad
        objective_dict["Quadratic"] = (
            np.eye(len(objective_dict["Linear"])) * self.regularization_weight
        )
        return objective_dict

    def get_constraints(self) -> Dict[str, np.ndarray]:
        """Get the constraints and computes them."""
        constraints_dict = super().get_constraints()
        # FIXME: #11 Implement MAD constraints
        mean_mat = np.tile(self.returns.mean(), (self.num_obs, 1))
        mad_ge = np.concatenate(
            (
                self.returns - mean_mat,
                -np.eye(self.num_obs),
            ),
            axis=1,
        )
        mad_le = np.concatenate(
            (
                -(self.returns - mean_mat),
                -np.eye(self.num_obs),
            ),
            axis=1,
        )
        positive_abs_dev = np.concatenate(
            (
                np.zeros(shape=(self.num_obs, self.num_assets)),
                -np.eye(self.num_obs),
            ),
            axis=1,
        )
        h_mad = np.zeros(3 * self.num_obs)
        if ConstraintType.NO_SHORTSELLING in self.constraints:
            constraints_dict["G_inequality"] = np.concatenate(
                (
                    mad_ge,
                    mad_le,
                    positive_abs_dev,
                    super().get_constraints()["G_inequality"],
                )
            )
            constraints_dict["h_inequality"] = np.hstack(
                (
                    h_mad,
                    super().get_constraints()["h_inequality"],
                )
            )
        else:
            constraints_dict["G_inequality"] = np.concatenate(
                (
                    mad_ge,
                    mad_le,
                    positive_abs_dev,
                )
            )
            constraints_dict["h_inequality"] = h_mad

        # TODO: #10 Add other constraints
        return constraints_dict


class MeanCVaR(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: float = 0.05,
        cash_pct: float = 0,
        confidence_level: float = 0.05,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )
        self.confidence_level = confidence_level

    @property
    def objective_function(self) -> Dict[str, np.ndarray]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        Linear
            Linear objective function
        Quadratic
            Quadratoc objective function
        """
        objective_dict = super().objective_function
        w = np.zeros(self.num_assets)
        dev_from_zeta = np.ones(self.num_obs) / (self.confidence_level * self.num_obs)
        zeta = 1.0
        linear_cvar = np.hstack((w, dev_from_zeta, zeta))
        objective_dict["Linear"] = linear_cvar
        objective_dict["Quadratic"] = (
            np.eye(len(objective_dict["Linear"])) * self.regularization_weight
        )
        return objective_dict

    def get_constraints(self) -> Dict[str, np.ndarray]:
        """Get the constraints and computes them."""
        constraints_dict = super().get_constraints()
        cvar_ge = np.concatenate(
            (
                -self.returns,
                -np.eye(self.num_obs),
                -np.ones((self.num_obs, 1)),
            ),
            axis=1,
        )
        positive_dev_from_zeta = np.concatenate(
            (
                np.zeros(shape=(self.num_obs, self.num_assets)),
                -np.eye(self.num_obs),
                np.zeros((self.num_obs, 1)),
            ),
            axis=1,
        )
        h_cvar = np.zeros(2 * self.num_obs)
        if ConstraintType.NO_SHORTSELLING in self.constraints:
            constraints_dict["G_inequality"] = np.concatenate(
                (
                    cvar_ge,
                    positive_dev_from_zeta,
                    super().get_constraints()["G_inequality"],
                )
            )
            constraints_dict["h_inequality"] = np.hstack(
                (
                    h_cvar,
                    super().get_constraints()["h_inequality"],
                )
            )
        else:
            constraints_dict["G_inequality"] = np.concatenate(
                (
                    cvar_ge,
                    positive_dev_from_zeta,
                )
            )
            constraints_dict["h_inequality"] = h_cvar
        # TODO: #10 Add other constraints
        return constraints_dict


class OptimizationProblem(OptimizationModel):
    """Class that selects the optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        regularization_weight: float = 0.05,
        cash_pct: float = 0.0,
        confidence_level: float = 0.05,
    ) -> None:
        super().__init__(
            returns, objective_type, constraints, regularization_weight, cash_pct
        )
        if self.objective_type == ObjectiveType.VARIANCE:
            self.model = MeanVariance(  # type: ignore
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                regularization_weight=self.regularization_weight,
                cash_pct=self.cash_pct,
            )
        if self.objective_type == ObjectiveType.MAD:
            self.model = MeanMAD(  # type: ignore
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                regularization_weight=self.regularization_weight,
                cash_pct=self.cash_pct,
            )
        if self.objective_type == ObjectiveType.CVAR:
            self.confidence_level = confidence_level or 0.05
            self.model = MeanCVaR(  # type: ignore
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                regularization_weight=self.regularization_weight,
                cash_pct=self.cash_pct,
                confidence_level=self.confidence_level,
            )

    @property
    def objective_function(self) -> Dict[str, np.ndarray]:
        return self.model.objective_function

    def get_constraints(self) -> Dict[str, np.ndarray]:
        """Get the constraints and computes them."""
        return self.model.get_constraints()

    def solve(self) -> OptimalPortfolio:
        """Solves the following optimization problem.

        minimize:
                    (1/2)*x'*P*x + q'*x
        subject to:
                    G*x <= h
                    A*x = b.
        """
        return self.model.solve()
