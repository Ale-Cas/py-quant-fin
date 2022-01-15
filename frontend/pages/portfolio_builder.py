"""
Created on Jan 11, 2022
@author: AC

This module provides the streamlit UI to build your customized portfolio.
"""
import streamlit as st
from streamlit.elements.dataframe_selector import DataFrameSelectorMixin

from quantfin.market import assets, data_download

title = "Portfolio Builder"


def app() -> None:
    """This app renders the Portfolio Builder page"""
    # TEXT:
    st.write(
        """
             # Portfolio Builder
             
             Please choose an investment universe and a portfolio selection strategy.
             Then provide the parameters on the sidebar to customize your portfolio.
             """
    )

    # INPUTs:

    investment_univ = st.text_input(label="Enter an investment universe", value="SP500")
    ptf_strategy = st.text_input(
        label="Enter a portfolio selection strategy", value="SP500"
    )

    st.sidebar.title("Parameters")

    mu = st.sidebar.number_input(
        label="Choose a level of risk appetite", min_value=0.0, max_value=1.0
    )
