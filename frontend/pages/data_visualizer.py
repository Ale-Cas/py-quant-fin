"""
Created on Jan 13, 2022
@author: AC

This module provides the streamlit UI to download customized stock data.
"""
import streamlit as st
from streamlit.elements.dataframe_selector import DataFrameSelectorMixin

from quantfin.market import assets, data_download

title = "Data Visualization"


def app() -> None:
    """This app renders the Data Analyzer page"""
    # TEXT:
    st.write(
        """
             # Data Analysis Dashboard
             
             Please provide an asset ticker to display historical data.
             """
    )

    # INPUTs:
    st.sidebar.title("Parameters")

    asset_class = st.sidebar.selectbox(
        label="Choose an asset class", options=("Equity", "Fixed-Income", "ETF")
    )
    asset_ticker = st.text_input(label="Enter an asset ticker", value="AAPL")
    data_provider = st.sidebar.selectbox(
        label="Choose a data provider", options=("Yahoo Finance", "Others")
    )

    # PROCESSING:
    if asset_class == "Equity":
        asset = assets.Stock(
            ticker=asset_ticker,
            data_provider=data_provider,
        )
    else:
        raise NotImplementedError("Not implemented yet.")

    if asset.data_provider == "Yahoo Finance":
        asset.prices = data_download.YahooDownloader.get_prices(ticker=asset_ticker)
    else:
        raise NotImplementedError("Not implemented yet.")

    # OUTPUT:
    st.write(
        """
             ### Closing Prices
        """
    )
    st.line_chart(asset.prices["Close"])

    st.write(
        """
             ### Volume
        """
    )
    st.line_chart(asset.prices["Volume"])
