"""This module implements severl option pricing modules."""
from abc import ABC
from datetime import timedelta

import numpy as np
import pandas as pd
from scipy import stats

from quantfin.utils import ListEnum


class OptionTypes(ListEnum):
    """List Enum of option types."""

    CALL = "Call"
    PUT = "Put"


class OptionPricingModels(ListEnum):
    """List Enum of supported pricing models."""

    BINOMIAL = "Cox-Ross-Rubinstein Binomial Tree"
    BSM = "Black-Scholes-Merton Model"


class PricingModel(ABC):
    """Abstract base class for pricing models."""

    def __init__(
        self,
        underlying_prices: pd.Series,
        strike_price: float,
        expiry_date: pd.Timestamp,
        risk_free_rate: float = 0.001,
    ) -> None:
        self.underlying_prices = underlying_prices
        self.strike_price = strike_price
        self.expiry_date = expiry_date
        self.risk_free_rate = risk_free_rate

    @property
    def last_price(self) -> float:
        """Returns the prices Series last observation as an instance attribute."""
        return self.underlying_prices.iloc[-1, :]

    @property
    def volatility(self) -> float:
        """Returns the prices Series standard deviation as an instance attribute."""
        return np.sqrt(self.underlying_prices.var(numeric_only=True))

    @property
    def days_to_expiry(self) -> int:
        """Returns the days to expiry."""
        today = pd.to_datetime("today").date()
        difference: timedelta = self.expiry_date.date() - today
        return difference.days


class BlackScholes(PricingModel):
    """Black-Scholes-Merton model implementation"""

    def __init__(
        self,
        underlying_prices: pd.Series,
        strike_price: float,
        expiry_date: pd.Timestamp,
        risk_free_rate: float = 0.001,
    ) -> None:
        super().__init__(underlying_prices, strike_price, expiry_date, risk_free_rate)

    @property
    def d1(self) -> float:
        """Returns the d1 parameter as an instance attribute."""
        return np.log(self.last_price / self.expiry_date) + (
            self.risk_free_rate + (self.volatility ** 2) / 2.0 * self.days_to_expiry
        ) / (self.volatility * np.sqrt(self.days_to_expiry))

    @property
    def d2(self) -> float:
        """Returns the d1 parameter as an instance attribute."""
        return self.d1 - self.volatility * np.sqrt(self.days_to_expiry)

    def calculate_option_price(
        self,
        option_type: OptionTypes = OptionTypes.CALL.value,
    ) -> float:
        """Returns the option price."""
        if option_type == OptionTypes.CALL.value:
            option_price = self.last_price * stats.norm.cdf(
                self.d1
            ) - self.strike_price * np.exp(
                -self.risk_free_rate * self.days_to_expiry
            ) * stats.norm.cdf(
                self.d2
            )
        if option_type == OptionTypes.PUT.value:
            option_price = -self.last_price * stats.norm.cdf(
                -self.d1
            ) + self.strike_price * np.exp(
                -self.risk_free_rate * self.days_to_expiry
            ) * stats.norm.cdf(
                -self.d2
            )
        return option_price
