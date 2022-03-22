"""Module to implement optimization problems."""
from typing import Dict, Set, Optional

import cvxopt as opt
import numpy as np

from quantfin.market import assets
from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio import OptimalPortfolio
from quantfin.portfolio_selection.strategy import (
    PortfolioSelectionModel,
    PortfolioSelectionProblem,
)
from quantfin.utils import ListEnum


class ObjectiveFunction(str, ListEnum):
    """List of objective functions."""

    VARIANCE = "Variance"
    MAD = "Mean-Absolute-Deviation"
    CVAR = "Conditional-Value-at-Risk"


class Constraint(str, ListEnum):
    """List of constraints."""

    NO_SHORTSELLING = "No short-selling"
    MAX_INSTR_WEIGHT = "Maximum instrument weight"


class OptimizationModel(PortfolioSelectionModel):
    """Class that represents a portfolio optimization model.

    Parameters
    ----------

    constraints: Optional[Set[Constraint]]
        The constraints that the optimization model has to satisfy.
    """

    def __init__(
        self,
        constraints: Optional[Set[Constraint]] = None,
    ) -> None:
        super().__init__()
        if constraints is not None:
            for constraint in constraints:
                if not isinstance(constraint, Constraint):
                    raise ValueError("All the constraints must be of type Constraint")
        self.constraints = constraints

    def add_constraint(self, constraint: Constraint) -> None:
        """Instance method to add a constraint to the set of constraints.

        Parameters
        ----------
        constraint: Constraint
        """
        if not isinstance(constraint, Constraint):
            raise ValueError("All the constraints must be of type Constraint")
        if self.constraints is None:
            self.constraints = set()
        self.constraints.add(constraint)

    def del_constraint(self, constraint: Constraint) -> None:
        """Instance method to remove a constraint to the set of constraints.

        Parameters
        ----------
        constraint: Constraint
        """
        assert self.constraints, "There are no constraints."
        if not isinstance(constraint, Constraint):
            raise ValueError("All the constraints must be of type Constraint")
        assert (
            constraint in self.constraints
        ), "The constraint is not in the set of constraints"
        self.constraints.remove(constraint)

    def _compute_objective(
        self, investment_universe: InvestmentUniverse
    ) -> Dict[str, np.ndarray]:
        objective_dict: Dict[str, np.ndarray] = dict()
        objective_dict["Linear"] = np.zeros(
            shape=(investment_universe.num_ret_assets, 1)
        )
        objective_dict["Quadratic"] = np.zeros(
            shape=(
                investment_universe.num_ret_assets,
                investment_universe.num_ret_assets,
            )
        )  # TODO: change default quadratic
        return objective_dict

    def _compute_constraints(
        self,
        investment_universe: InvestmentUniverse,
        cash_pct: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        constraints_dict: Dict[str, np.ndarray] = dict()
        A_budget = np.hstack(
            (
                np.ones(investment_universe.num_ret_assets),
                np.zeros(
                    len(
                        self._compute_objective(investment_universe=investment_universe)[
                            "Linear"
                        ]
                    )
                    - investment_universe.num_ret_assets
                ),
            )
        )
        constraints_dict["A_budget"] = np.reshape(A_budget, (1, len(A_budget)))
        constraints_dict["b_budget"] = (1.0 - cash_pct) * np.ones(
            1
        )  # to make mypy happy
        if self.constraints:
            if Constraint.NO_SHORTSELLING in self.constraints:

                G_no_short = np.concatenate(
                    (
                        -np.eye(investment_universe.num_ret_assets),
                        np.zeros(
                            (
                                investment_universe.num_ret_assets,
                                len(
                                    self._compute_objective(
                                        investment_universe=investment_universe
                                    )["Linear"]
                                )
                                - investment_universe.num_ret_assets,
                            )
                        ),
                    ),
                    axis=1,
                )
                h_no_short = np.zeros(investment_universe.num_ret_assets)
                constraints_dict["G_inequality"] = G_no_short
                constraints_dict["h_inequality"] = h_no_short
        return constraints_dict

    def compute_optimal_portfolio(
        self,
        investment_universe: InvestmentUniverse,
        cash_pct: float = 0.0,
    ) -> OptimalPortfolio:
        """Solves the following optimization problem.

        minimize:
                    (1/2)*x'*P*x + q'*x
        subject to:
                    G*x <= h
                    A*x = b.
        """
        _objectives_dict = self._compute_objective(
            investment_universe=investment_universe
        )
        _constraints_dict = self._compute_constraints(
            investment_universe=investment_universe,
            cash_pct=cash_pct,
        )
        objectives_matrices = {
            name: opt.matrix(objective) for name, objective in _objectives_dict.items()
        }
        constraints_matrices = {
            name: opt.matrix(constraint)
            for name, constraint in _constraints_dict.items()
        }
        try:
            if (
                self.constraints is None
                or not Constraint.NO_SHORTSELLING in self.constraints
            ):
                if "Quadratic" in objectives_matrices:
                    # Solve Quadratic Programming Problem
                    solution = opt.solvers.qp(
                        P=objectives_matrices["Quadratic"],
                        q=objectives_matrices["Linear"],
                        A=constraints_matrices["A_budget"],
                        b=constraints_matrices["b_budget"],
                    )
                else:
                    # Solve Linear Programming Problem
                    solution = opt.solvers.lp(
                        c=objectives_matrices["Linear"],
                        A=constraints_matrices["A_budget"],
                        b=constraints_matrices["b_budget"],
                    )
            if "Quadratic" in objectives_matrices:
                # Solve Quadratic Programming Problem
                solution = opt.solvers.qp(
                    P=objectives_matrices["Quadratic"],
                    q=objectives_matrices["Linear"],
                    G=constraints_matrices["G_inequality"],
                    h=constraints_matrices["h_inequality"],
                    A=constraints_matrices["A_budget"],
                    b=constraints_matrices["b_budget"],
                )
            else:
                # Solve Linear Programming Problem
                solution = opt.solvers.lp(
                    c=objectives_matrices["Linear"],
                    G=constraints_matrices["G_inequality"],
                    h=constraints_matrices["h_inequality"],
                    A=constraints_matrices["A_budget"],
                    b=constraints_matrices["b_budget"],
                )
        except ValueError as ve:
            raise ve
        assert (
            solution["status"] == "optimal"
        ), "The status of the solution is not optimal!"
        weights = np.array(solution["x"]).reshape(np.array(solution["x"]).size)[
            0 : investment_universe.num_ret_assets
        ]
        stocks = []
        for ticker in investment_universe.assets:
            stocks.append(assets.Stock(ticker=ticker))
        opt_holdings: Dict[assets.Asset, float] = dict(zip(stocks, weights))

        for asset, weight in opt_holdings.items():
            if weight > 0 and weight < 1e-4:
                opt_holdings[asset] = 0.0
        return OptimalPortfolio(
            name=f"{self.__class__.__name__} Portfolio",
            holdings=opt_holdings,
            assets_returns=investment_universe.returns,
            optimization_model_name=self.__class__.__name__,
        )


class MeanVariance(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def _compute_objective(
        self, investment_universe: InvestmentUniverse
    ) -> Dict[str, np.ndarray]:
        return {
            "Quadratic": 2 * investment_universe.returns.cov().values,
            "Linear": np.zeros(shape=(investment_universe.num_ret_assets, 1)),
        }

    def _compute_constraints(
        self,
        investment_universe: InvestmentUniverse,
        cash_pct: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        constraints_dict = super()._compute_constraints(
            investment_universe=investment_universe,
            cash_pct=cash_pct,
        )
        constraints_dict["A_budget"] = np.ones(
            shape=(1, investment_universe.num_ret_assets)
        )
        if self.constraints:
            if Constraint.NO_SHORTSELLING in self.constraints:
                constraints_dict["G_inequality"] = -np.eye(
                    investment_universe.num_ret_assets
                )
        return constraints_dict


class MeanMAD(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def _compute_objective(
        self, investment_universe: InvestmentUniverse
    ) -> Dict[str, np.ndarray]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        Linear
            Linear objective function
        """
        (t, n_assets) = np.shape(investment_universe.returns.values)
        linear_mad = np.hstack(
            (
                np.zeros(n_assets),
                np.ones(t) / t,
            )
        )
        linear_mad = linear_mad.reshape(-1, 1)
        objective_dict: Dict[str, np.ndarray] = dict()
        objective_dict["Linear"] = linear_mad
        return objective_dict

    def _compute_constraints(
        self,
        investment_universe: InvestmentUniverse,
        cash_pct: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        constraints_dict = super()._compute_constraints(
            investment_universe=investment_universe,
            cash_pct=cash_pct,
        )
        mean_mat = np.tile(
            investment_universe.returns.mean(), (investment_universe.num_obs_returns, 1)
        )
        mad_ge = np.concatenate(
            (
                investment_universe.returns - mean_mat,
                -np.eye(investment_universe.num_obs_returns),
            ),
            axis=1,
        )
        mad_le = np.concatenate(
            (
                -(investment_universe.returns - mean_mat),
                -np.eye(investment_universe.num_obs_returns),
            ),
            axis=1,
        )
        positive_abs_dev = np.concatenate(
            (
                np.zeros(
                    shape=(
                        investment_universe.num_obs_returns,
                        investment_universe.num_ret_assets,
                    )
                ),
                -np.eye(investment_universe.num_obs_returns),
            ),
            axis=1,
        )
        h_mad = np.zeros(3 * investment_universe.num_obs_returns)
        if self.constraints:
            if Constraint.NO_SHORTSELLING in self.constraints:
                constraints_dict["G_inequality"] = np.concatenate(
                    (
                        mad_ge,
                        mad_le,
                        positive_abs_dev,
                        constraints_dict["G_inequality"],
                    )
                )
                constraints_dict["h_inequality"] = np.hstack(
                    (
                        h_mad,
                        constraints_dict["h_inequality"],
                    )
                )
                self.constraints_dict = constraints_dict
        else:
            constraints_dict["G_inequality"] = np.concatenate(
                (
                    mad_ge,
                    mad_le,
                    positive_abs_dev,
                )
            )
            constraints_dict["h_inequality"] = h_mad
        return constraints_dict


class MeanCVaR(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    def __init__(
        self,
        constraints: Optional[Set[Constraint]] = None,
        confidence_level: float = 0.05,
    ) -> None:
        super().__init__(constraints)
        self.confidence_level = confidence_level

    def _compute_objective(
        self, investment_universe: InvestmentUniverse
    ) -> Dict[str, np.ndarray]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        Linear
            Linear objective function
        Quadratic
            Quadratoc objective function
        """
        objective_dict: Dict[str, np.ndarray] = dict()
        w = np.zeros(investment_universe.num_ret_assets)
        dev_from_zeta = np.ones(investment_universe.num_obs_returns) / (
            self.confidence_level * investment_universe.num_obs_returns
        )
        zeta = 1.0
        linear_cvar = np.hstack((w, dev_from_zeta, zeta))
        linear_cvar = np.array([linear_cvar]).transpose()
        # linear_cvar = linear_cvar.reshape(-1, 1)
        objective_dict["Linear"] = linear_cvar
        return objective_dict

    def _compute_constraints(
        self,
        investment_universe: InvestmentUniverse,
        cash_pct: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        constraints_dict = super()._compute_constraints(
            investment_universe=investment_universe,
            cash_pct=cash_pct,
        )
        cvar_ge = np.concatenate(
            (
                -investment_universe.returns,
                -np.eye(investment_universe.num_obs_returns),
                -np.ones((investment_universe.num_obs_returns, 1)),
            ),
            axis=1,
        )
        positive_dev_from_zeta = np.concatenate(
            (
                np.zeros(
                    shape=(
                        investment_universe.num_obs_returns,
                        investment_universe.num_ret_assets,
                    )
                ),
                -np.eye(investment_universe.num_obs_returns),
                np.zeros((investment_universe.num_obs_returns, 1)),
            ),
            axis=1,
        )
        h_cvar = np.zeros(2 * investment_universe.num_obs_returns)
        if self.constraints:
            if Constraint.NO_SHORTSELLING in self.constraints:
                constraints_dict["G_inequality"] = np.concatenate(
                    (
                        cvar_ge,
                        positive_dev_from_zeta,
                        constraints_dict["G_inequality"],
                    )
                )
                constraints_dict["h_inequality"] = np.hstack(
                    (
                        h_cvar,
                        constraints_dict["h_inequality"],
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
        return constraints_dict


class OptimizationProblem(PortfolioSelectionProblem):
    """Class that defines the optimization problem."""

    def __init__(
        self,
        optimization_model: OptimizationModel,
        investment_universe: InvestmentUniverse,
    ) -> None:
        self.optimization_model = optimization_model
        super().__init__(
            portfolio_selection_model=self.optimization_model,
            investment_universe=investment_universe,
        )

    def solve(self) -> OptimalPortfolio:
        """Solve the specified Portfolio Selection Problem and return an OptimalPortfolio object."""
        return self.optimization_model.compute_optimal_portfolio(
            investment_universe=self.investment_universe,
        )
