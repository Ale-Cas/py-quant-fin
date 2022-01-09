"""
The data_sources module provides dataclasses for supported data providers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DataProviders:
    """Abstraction for data providers."""

    name: str = "Yahoo Finance"
    python_wrapper: bool = True
    wrapper_name: str = "yfinance"
    is_official_wrapper: bool = False

    def __hash__(self) -> int:
        return hash(self.name)
