"""
Created on Jan 13, 2022
@author: AC

This module provides the streamlit UI to download customized stock data.
"""
from click import option
import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf


from quantfin.market.assets import AssetClasses, Stock
from quantfin.market.investment_universe import scrape_largest_companies

title = "Dashboard"


def app() -> None:
    """This app renders the Data Analyzer page"""
    # TEXT:
    st.write(
        """
             # Data Analysis Dashboard
             
             Please provide an asset name to display historical data.
             """
    )

    # INPUTs:
    st.sidebar.title("Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
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
        period = st.sidebar.selectbox(
            label="Period",
            options=[
                "max",
                "ytd",
                "10y",
                "5y",
                "2y",
                "1y",
                "1d",
                "5d",
                "1mo",
                "3mo",
                "6mo",
            ],
        )
        interval = st.sidebar.selectbox(
            label="Interval",
            options=[
                "1d",
                "1h",
                "5d",
                "1wk",
                "1mo",
                "3mo",
            ],
        )
        with st.spinner("Getting companies..."):
            companies_df = get_global_stocks(
                hundred_results=int(np.ceil(number_of_stocks / 100))
            )
        with col2:
            country = st.selectbox(
                label="Choose a country", options=companies_df["country"].unique()
            )
        with col3:
            stock_name = st.selectbox(
                label="Choose a stock",
                options=companies_df.loc[companies_df["country"] == str(country)][
                    "name"
                ],
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

        @st.cache(persist=True, allow_output_mutation=True)
        def get_prices(
            stock: Stock, period: str = "max", interval: str = "1d"
        ) -> pd.DataFrame:
            """Get prices from Yahoo Finance"""
            return yf.Ticker(ticker=stock.ticker).history(
                period=period, interval=interval
            )

        with st.spinner("Getting prices..."):
            stock.prices = get_prices(stock=stock, period=period, interval=interval)

        @st.cache(persist=True, allow_output_mutation=True)
        def get_info(stock: Stock) -> dict:
            return yf.Ticker(ticker=stock.ticker).info

        @st.cache(persist=True, allow_output_mutation=True)
        def get_news(stock: Stock) -> dict:
            return yf.Ticker(ticker=stock.ticker).news

    else:
        raise NotImplementedError("Not implemented yet.")

    # OUTPUT:
    with st.spinner("Getting company info..."):
        info = get_info(stock=stock)
    st.write(
        """
             ## Business Summary
        """
    )
    with st.expander("See business description"):
        st.write(info["longBusinessSummary"])
    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        st.write("**Ticker**: ", stock.ticker)
        st.write("**Website**: ", info["website"])
    with col_2:
        st.write("**Sector**: ", info["sector"])
        st.write("**Industry**: ", info["industry"])
    with col_3:
        st.write(
            "**Number of shares**: ",
            str(round(info["sharesOutstanding"] / 1e6, 2)),
            "milions",
        )
        st.write("**Market beta**: ", str(round(info["beta"], 2)))
    st.write("## Prices")
    st.line_chart(stock.prices[["Open", "High", "Low", "Close"]])
    st.line_chart(stock.prices["Volume"])
    if interval != "1h":
        try:
            stock.prices.index = stock.prices.index.date
        except AttributeError:
            pass
    st.dataframe(stock.prices)
    # st.write(get_info(stock=stock))
    news: list[dict] = get_news(stock=stock)
    st.write("## Related news:")
    for n in news:
        st.markdown(f"[{n.get('title')}]({n.get('link')})")
