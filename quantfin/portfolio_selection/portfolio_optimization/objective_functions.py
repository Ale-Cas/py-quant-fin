"""Module to implement objective functions."""
from abc import ABC, abstractmethod
from typing import Any, Optional

import numpy as np
import pandas as pd
import cvxopt as opt

from quantfin.utils import ListEnum


class ObjectiveFunctions(str, ListEnum):
    """List of basic objective functions."""

    VARIANCE = "Covariance Matrix"
    MAD = "Linearized Mean-Absolute-Deviation"
    CVAR = "Linearized Conditional-Value-at-Risk"


class IObjectiveFunction(ABC):
    """Interface for objective functions."""

    @abstractmethod
    def __init__(
        self,
        name: str,
        returns: pd.DataFrame,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.returns = returns
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

    @abstractmethod
    def __call__(self) -> opt.matrix:
        pass

    @abstractmethod
    def has_auxiliary_variables(self) -> bool:
        """Returns True
        if the objective function has auxiliary variables
        and False otherwise"""
        pass


class CovarianceMatrix(IObjectiveFunction):
    """Covariance Matrix as an objective function."""

    def __init__(self, returns: pd.DataFrame) -> None:
        super().__init__(
            name=ObjectiveFunctions.VARIANCE.value,
            returns=returns,
        )

    def _is_positive_semidefinite(self) -> bool:
        """Check if the returns dataframe is a positive definite matrix."""
        try:
            # Significantly more efficient than checking eigenvalues (stackoverflow.com/questions/16266720)
            np.linalg.cholesky(self.returns + 1e-16 * np.eye(len(self.returns)))
            return True
        except np.linalg.LinAlgError:
            return False

    def __call__(self) -> opt.matrix:
        """Returns the objective as cvxopt.qp() wants it."""
        if self._is_positive_semidefinite:
            return opt.matrix(2 * self.returns.cov().values)
        else:
            raise ValueError("The returns matrix is not positive semidefinite!")

    def has_auxiliary_variables(self) -> bool:
        """Returns True
        if the objective function has auxiliary variables
        and False otherwise"""
        return False


class LinearMAD(IObjectiveFunction):
    """Linearized Mean Absolute Deviation."""

    def __init__(self, returns: pd.DataFrame) -> None:
        super().__init__(
            name=ObjectiveFunctions.MAD.value,
            returns=returns,
        )

    def __call__(self) -> opt.matrix:
        """Returns the objective as cvxopt.qp() wants it."""
        (num_obs, num_assets) = np.shape(self.returns)
        linear_mad = np.hstack((np.zeros(num_assets), np.ones(num_obs) / num_obs))
        return opt.matrix(linear_mad)

    def has_auxiliary_variables(self) -> bool:
        """Returns True
        if the objective function has auxiliary variables
        and False otherwise"""
        return True


class LinearCVaR(IObjectiveFunction):
    """Linearized Conditional Value-at-Risk."""

    def __init__(self, returns: pd.DataFrame, confidence_level: float = 0.05) -> None:
        super().__init__(
            name=ObjectiveFunctions.CVAR.value,
            returns=returns,
        )
        self.confidence_level = confidence_level

    def __call__(self) -> opt.matrix:
        """Returns the objective as cvxopt.qp() wants it."""
        (num_obs, num_assets) = np.shape(self.returns)
        linear_mad = np.hstack((np.zeros(num_assets), np.ones(num_obs) / num_obs))
        return opt.matrix(linear_mad)

    def has_auxiliary_variables(self) -> bool:
        """Returns True
        if the objective function has auxiliary variables
        and False otherwise"""
        return True
