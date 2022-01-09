"""Abstraction layer for Assets."""
from __future__ import annotations

import dataclasses
from typing import List, Optional, Union
from warnings import warn

import pandas as pd
import yfinance as yf

from quantfin.market.data_sources import DataProviders


@dataclasses.dataclass
class Cash:
    """This class represents Cash."""

    currency: str = "EUR"


class Asset:
    """
    This class represent a single asset.
    """

    _VALID_ASSET_CLASSES = {"Equity", "Fixed-Income", "Fund"}
    _VALID_DATA_PROVIDERS = {
        DataProviders(name="Yahoo Finance"),
    }

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        asset_class: Optional[str] = None,
        data_provider: DataProviders = None,
        prices: Optional[pd.DataFrame] = None,
    ) -> None:
        """
        Initialize the Asset.
        """
        self.name = name
        self.ticker = ticker
        self.isin = isin
        self.exchange = exchange

        if asset_class is None:
            # The default asset class is Equity
            self.asset_class = "Equity"
        elif asset_class in Asset._VALID_ASSET_CLASSES:
            self.asset_class = asset_class
        else:
            raise ValueError(
                f"The specified asset_class is not valid, use one of: {Asset._VALID_ASSET_CLASSES}"
            )

        if data_provider is None:
            # The default data provider is Yahoo Finance
            self.data_provider = DataProviders(name="Yahoo Finance")
        elif data_provider in Asset._VALID_DATA_PROVIDERS:
            self.data_provider = data_provider
        else:
            raise ValueError(
                f"""The specified data_provider is not supported, 
                use one of: {Asset._VALID_DATA_PROVIDERS}"""
            )
        self.prices = prices or pd.DataFrame()

    def get_prices(
        self,
        period: str = "max",
        interval: str = "1d",
        start: Union[str, pd.Timestamp] = None,
        end: Union[str, pd.Timestamp] = None,
        prepost_data: bool = False,
        auto_adjust=True,
        back_adjust=False,
    ) -> pd.DataFrame:
        """
        Get historical prices from the data source specified during the initialisation.

        Parameters
        ----------
        period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or pd.Timestamp.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or pd.Timestamp.
                Default is now
            prepost : bool
                Include Pre and Post market data in results?
                Default is False
            auto_adjust: bool
                Adjust all OHLC automatically? Default is True
            back_adjust: bool
                Back-adjusted data to mimic true historical prices (optional)


        Returns
        -------
        prices
            A pandas DataFrame containing historical prices for specified parameters
        """
        if self.prices is not None and self.prices.empty() is False:
            warn("Warning: prices DataFrame has already been defined!")
        if self.data_provider.name == "Yahoo Finance":
            self.prices = yf.Ticker(self.ticker).history(
                period=period,
                interval=interval,
                start=start,
                end=end,
                prepost=prepost_data,
                auto_adjust=auto_adjust,
                back_adjust=back_adjust,
            )
        return self.prices

    # def weight_in_ptf(
    #     self,
    #     portfolio: Portfolio,
    # ) -> Portfolio:
    #     """Retrieves the weight of the Asset in the specified Portfolio"""
    #     return portfolio


class Stock(Asset):
    """
    This class represent a single Stock.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        data_provider: DataProviders = None,
        prices: pd.DataFrame = None,
    ) -> None:
        """
        Initialize the Stock
        """
        super().__init__(
            name,
            ticker,
            isin,
            exchange,
            asset_class="Equity",
            data_provider=data_provider,
            prices=prices,
        )


class Bond(Asset):
    """
    This class represent a single Bond.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        data_provider: DataProviders = None,
        prices: pd.DataFrame = None,
    ) -> None:
        """
        Initialize the Bond
        """
        super().__init__(
            name,
            ticker,
            isin,
            exchange,
            asset_class="Fixed-Income",
            data_provider=data_provider,
            prices=prices,
        )


class ETF(Asset):
    """
    This class represent a single Exchanged Traded Fund.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        ticker: Optional[str] = None,
        isin: Optional[str] = None,  # International Securities Identification Number
        exchange: Optional[str] = None,
        data_provider: Optional[DataProviders] = None,
        prices: pd.DataFrame = None,
        ref_index: Optional[str] = None,
        components: List[Union[Stock, Bond]] = None,
    ) -> None:
        """
        Initialize the ETF
        """
        super().__init__(
            name,
            ticker,
            isin,
            exchange,
            asset_class="Fund",
            data_provider=data_provider,
            prices=prices,
        )
        self.ref_index = ref_index
        self.components = components
