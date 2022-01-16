"""Module to implement optimization problems."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import cvxopt as opt
import numpy as np
import pandas as pd

from quantfin.utils import ListEnum
from quantfin.market import assets
from quantfin.portfolio_selection.portfolio import OptimalPortfolio


class ObjectiveType(str, ListEnum):
    """List of objective functions."""

    VARIANCE = "Variance"
    MAD = "Mean-Absolute-Deviation"
    CVAR = "Conditional-Value-at-Risk"


class ConstraintType(ListEnum):
    """List of constraints."""

    NO_SHORTSELLING = "NO_SHORTSELLING"
    MAX_INSTRUMENT_WEIGHT = "MAX_INSTRUMENT_WEIGHT"


class OptimizationModel(ABC):
    """Class that represents an abstract optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
    ) -> None:
        self.returns = returns
        self.objective_type = objective_type
        self.constraints = constraints

    def add_constraint(self, constraint: ConstraintType) -> None:
        if isinstance(constraint, ConstraintType):
            self.constraints.append(constraint)
        else:
            raise ValueError(
                f"""The constraint type is not valid, 
                    supported constraints are: {",".join(ConstraintType.list())}"""
            )

    @abstractmethod
    def get_constraints(self) -> Any:
        raise NotImplementedError("Abstract method")

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
        constraints: List[ConstraintType] = [],
    ) -> None:
        super().__init__(returns, objective_type, constraints)

    def get_constraints(self) -> Dict[str, Union[np.array, float]]:
        """Get the constraints and computes them."""
        n: int = len(self.returns.columns)
        constraints_dict = {}

        # BUDGET:
        # Equality constraint A * x = b
        constraints_dict["A"] = np.ones(shape=(1, n))
        constraints_dict["b"] = 1.0

        if ConstraintType.NO_SHORTSELLING in self.constraints:
            # Inequality constraint G * x <= h
            constraints_dict["G"] = -np.eye(n)  # negative n x n identity matrix
            constraints_dict["h"] = np.zeros(shape=(n, 1))

        # TODO: #10 Add other constraints
        return constraints_dict

    @property
    def objective_function(self) -> Dict[str, Union[np.array, float]]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        P
            Quadratic part of the objective function
        q'
            Linear part (already transposed)
        """
        n: int = len(self.returns.columns)
        return {"P": 2 * self.returns.cov().values, "q'": np.zeros(shape=(n, 1))}

    def solve(self) -> OptimalPortfolio:
        """Solve the following optimization problem.

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
            P=objectives_matrices["P"],
            q=objectives_matrices["q'"],
            G=constraints_matrices["G"],
            h=constraints_matrices["h"],
            A=constraints_matrices["A"],
            b=constraints_matrices["b"],
        )
        n: int = len(self.returns.columns)
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
        (T, n) = np.shape(self.returns)
        constraints_dict = {}
        # FIXME: #11 Implement MAD constraints
        # BUDGET:
        # Equality constraint A * x = b
        constraints_dict["A"] = np.ones(shape=(1, n))
        constraints_dict["b"] = 1.0

        if ConstraintType.NO_SHORTSELLING in self.constraints:
            # Inequality constraint G * x <= h
            constraints_dict["G"] = -np.eye(n)  # negative n x n identity matrix
            constraints_dict["h"] = np.zeros(shape=(n, 1))

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
        (T, n) = np.shape(self.returns)
        linear_mad = np.hstack((np.zeros(n), np.ones(T) / T))
        return {"q": linear_mad}

    def solve(self) -> OptimalPortfolio:
        """Solve the following optimization problem.

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
            P=objectives_matrices["P"],
            q=objectives_matrices["q"],
            G=constraints_matrices["G"],
            h=constraints_matrices["h"],
            A=constraints_matrices["A"],
            b=constraints_matrices["b"],
        )
        n: int = len(self.returns.columns)
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


class MeanCVaR(OptimizationModel):
    """Class that represents the Mean-Variance model."""

    # FIXME: #12 Implement CVaR model

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        confidence_level: float = 0.05,
    ) -> None:
        super().__init__(returns, objective_type, constraints)
        self.confidence_level = confidence_level

    def get_constraints(self) -> Dict[str, Union[np.array, float]]:
        """Get the constraints and computes them."""
        n: int = len(self.returns.columns)
        constraints_dict = {}

        # BUDGET:
        # Equality constraint A * x = b
        constraints_dict["A"] = np.ones(shape=(1, n))
        constraints_dict["b"] = 1.0

        if ConstraintType.NO_SHORTSELLING in self.constraints:
            # Inequality constraint G * x <= h
            constraints_dict["G"] = -np.eye(n)  # negative n x n identity matrix
            constraints_dict["h"] = np.zeros(shape=(n, 1))

        # TODO: #10 Add other constraints
        return constraints_dict

    @property
    def objective_function(self) -> Dict[str, Union[np.array, float]]:
        """Returns a dictionary with the objective function.

        Keys
        ----
        P
            Quadratic part of the objective function
        q'
            Linear part (already transposed)
        """
        n: int = len(self.returns.columns)
        return {"P": 2 * self.returns.cov().values, "q'": np.zeros(shape=(n, 1))}

    def solve(self) -> OptimalPortfolio:
        """Solve the following optimization problem.

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
            P=objectives_matrices["P"],
            q=objectives_matrices["q"],
            G=constraints_matrices["G"],
            h=constraints_matrices["h"],
            A=constraints_matrices["A"],
            b=constraints_matrices["b"],
        )
        n: int = len(self.returns.columns)
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


class OptimizationProblem(OptimizationModel):
    """Class that selects the optimization problem."""

    def __init__(
        self,
        returns: pd.DataFrame,
        objective_type: ObjectiveType,
        constraints: List[ConstraintType] = [],
        confidence_level: Optional[float] = None,
    ) -> None:
        super().__init__(returns, objective_type, constraints)

        if self.objective_type == ObjectiveType.VARIANCE:
            self.model = MeanVariance(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
            )
        if self.objective_type == ObjectiveType.MAD:
            self.model = MeanMAD(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
            )
        if self.objective_type == ObjectiveType.CVAR:
            self.confidence_level = confidence_level or 0.05
            self.model = MeanCVaR(
                returns=self.returns,
                objective_type=self.objective_type,
                constraints=self.constraints,
                confidence_level=self.confidence_level,
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
