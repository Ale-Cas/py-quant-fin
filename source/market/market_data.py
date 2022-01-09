"""
The market_data module provides classes for downloading prices from supported data_providers.
"""

from __future__ import annotations

from source.market.data_sources import DataProviders


class MarketData:
    def __init__(
        self,
        data_provider: DataProviders,
    ) -> None:
        self.data_provider = data_provider
