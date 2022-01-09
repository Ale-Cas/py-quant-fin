"""
Test data_sources module.
"""
from quantfin.market.data_sources import DataProviders


def test_data_providers() -> None:
    provider = DataProviders()
    assert isinstance(provider, DataProviders)
