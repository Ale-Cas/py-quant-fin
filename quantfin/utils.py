"""This module provides utilities."""
from enum import Enum
from typing import Any, List
import pandas as pd
import numpy as np


class ListEnum(Enum):
    """This class provides a method to list enums values."""

    @classmethod
    def list(cls) -> List[Any]:
        return list(map(lambda c: c.value, cls))


def prices_to_returns(prices: pd.DataFrame, log: bool = False):
    """
    Calculate the returns given prices.

    Parameters
    ----------
    :param prices: pd.DataFrame
        A pandas DataFrame with asset prices
    :param log: bool
        Whether to compute logarithmic returns
        Default is False -> linear returns
    Returns
    -------
        A pd.DataFrame with linear or logarithmic returns
    """
    if log:
        return np.log(1 + prices.pct_change())
    else:
        return prices.pct_change()
