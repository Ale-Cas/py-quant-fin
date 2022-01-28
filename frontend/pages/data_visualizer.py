"""
Created on Jan 13, 2022
@author: AC

This module provides the streamlit UI to download customized stock data.
"""
import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf

from quantfin.market.assets import AssetClasses, Stock
from quantfin.market.investment_universe import scrape_largest_companies

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

    asset_class = st.selectbox(
        label="Choose an asset class", options=AssetClasses.list()
    )
    # asset_ticker = st.text_input(label="Enter an asset ticker", value="AAPL")

    # PROCESSING:
    if asset_class == AssetClasses.STOCKS.value:

        @st.cache(persist=True)
        def get_global_stocks(hundred_results: int = 10) -> pd.DataFrame:
            """Get company name, ticker and country of top companies based on market cap.
            By default returns 1000 biggest companies, max is 5800.
            """
            return scrape_largest_companies(num_pages=hundred_results)

        number_of_stocks = st.sidebar.number_input(
            label="Number of stocks", min_value=100, max_value=5800, value=1000
        )
        companies_df = get_global_stocks(
            hundred_results=int(np.ceil(number_of_stocks / 100))
        )
        country = st.selectbox(
            label="Choose a country", options=companies_df["country"].unique()
        )
        stock_name = st.selectbox(
            label="Choose a stock",
            options=companies_df.loc[companies_df["country"] == str(country)]["name"],
        )
        stock = Stock(
            name=str(stock_name),
            ticker=companies_df.loc[companies_df["name"] == str(stock_name)][
                "ticker"
            ].iloc[0],
            country=companies_df.loc[companies_df["name"] == str(stock_name)][
                "country"
            ].iloc[0],
        )

        @st.cache(persist=True)
        def get_prices(stock: Stock, period: str = "max") -> pd.DataFrame:
            """Get prices from Yahoo Finance"""
            return yf.Ticker(ticker=stock.ticker).history(period=period)

        stock.prices = get_prices(stock=stock)

    else:
        raise NotImplementedError("Not implemented yet.")

    # OUTPUT:
    st.write(
        """
             ### Closing Prices
        """
    )
    st.line_chart(stock.prices["Close"])

    st.write(
        """
             ### Volume
        """
    )
    st.line_chart(stock.prices["Volume"])
