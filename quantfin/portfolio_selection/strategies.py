"""Abstraction layer for Portfolio Strategies."""

from quantfin.utils import ListEnum


class PortfolioStrategies(ListEnum):
    PTF_OPT = "Portfolio Optimization"
    RISK_PARITY = "Risk Parity"
