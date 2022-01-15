"""Module to implement objective functions."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd
import cvxopt as opt


class ObjectiveFunctionType(str, Enum):
    """List of objective types."""

    MIN_VARIANCE = "Minimum Variance"
    MIN_MAD = "Minimum Mean-Absolute-Deviation"
    MIN_CVAR = "Minimum Conditional-Value-at-Risk"


class IObjectiveFunction(ABC):
    """Interface for objective functions."""

    @abstractmethod
    def __init__(
        self,
        name,
        **parameters,
    ) -> None:
        pass

    def __call__(self) -> Any:
        pass


class CovarianceMatrix(IObjectiveFunction):
    """Covariance Matrix as an objective function."""

    def __init__(self, returns: pd.DataFrame, **parameters) -> None:
        super().__init__(
            name="Covariance Matrix",
            **parameters,
        )
        self.returns = returns

    def _is_positive_semidefinite(self) -> bool:
        """Check if the returns dataframe is a positive definite matrix."""
        try:
            # Significantly more efficient than checking eigenvalues (stackoverflow.com/questions/16266720)
            np.linalg.cholesky(self.returns + 1e-16 * np.eye(len(self.returns)))
            return True
        except np.linalg.LinAlgError:
            return False

    def __call__(self) -> opt.matrix:
        """Returns the objective as cvxopt.qp wants it."""
        if self._is_positive_semidefinite:
            return opt.matrix(2 * self.returns.cov().values)
        else:
            raise ValueError("The returns matrix is not positive semidefinite!")
