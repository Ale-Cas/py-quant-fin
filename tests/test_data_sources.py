"""
Tests data_sources module.
"""
from source.market.data_sources import DataProviders


def test_data_providers() -> None:
    provider = DataProviders()
    assert isinstance(provider, DataProviders)
