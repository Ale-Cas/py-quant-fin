"""Modules for constraints."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import cvxopt as opt


class ConstraintType(Enum):
    BUDGET = "BUDGET"
    NO_SHORTSELLING = "NO_SHORTSELLING"
    MAX_INSTRUMENT_WEIGHT = "MAX_INSTRUMENT_WEIGHT"


class IConstraint(ABC):
    """This is an abstract interface to build multiple kinds of constraints."""

    @abstractmethod
    def __call__(
        self,
        num_assets: int,
        num_auxiliary_variables: int = 0,
    ) -> Dict[str, opt.matrix]:
        pass


class Budget(IConstraint):
    """This class makes portfolio weights sum to one."""

    def __call__(
        self,
        num_assets: int,
        # num_auxiliary_variables: int = 0,
    ) -> Dict[str, opt.matrix]:
        """Returns the constraint to make weghts sum to one
        as an equality constraint
        with a dictionary of cvxopt matrices.

        minimize f(x)
        s.t.
            A*x = b

        Returns
        -------
        equality_constraint
            Dict[str, opt.matrix] with keys: G, h where
            A = n x 1 vector of ones
            b = 1 x 1 matrix with the float 1.0
        """
        equality_constraint = {
            "A": opt.matrix(1.0, (1, num_assets)),
            "b": opt.matrix(1.0),
        }
        return equality_constraint


class NoShortSelling(IConstraint):
    """This class makes portfolio weights positive."""

    def __call__(
        self,
        num_assets: int,
        # num_auxiliary_variables: int = 0,
    ) -> Dict[str, opt.matrix]:
        """Returns the no shortselling constraint as an inequality constraint
        with a dictionary of cvxopt matrices.

        minimize f(x)
        s.t.
            G*x <= h

        Returns
        -------
        inequality_constraint
            Dict[str, opt.matrix] with keys: G, h where
            G = negative n x n identity matrix
            h = n x 1 vector of zeros
        """
        inequality_constraint = {
            "G": -opt.matrix(np.eye(num_assets)),
            "h": opt.matrix(0.0, (num_assets, 1)),
        }
        return inequality_constraint


class Constraints:
    def __init__(
        self,
        constraints_list: List[ConstraintType],
        num_assets: int,
        num_auxiliary_variables: Optional[int] = None,
    ) -> None:
        self.constraints_list = constraints_list
        self.num_assets = num_assets
        self.num_auxiliary_variables = num_auxiliary_variables

    def __call__(self) -> Dict[str, opt.matrix]:
        for con in self.constraints_list:
            if con == ConstraintType.BUDGET:
                budget_constraint = Budget(self.num_assets)

    def add_constraint(self, constraint_type: ConstraintType) -> None:
        self.constraints_list.append(constraint_type)
