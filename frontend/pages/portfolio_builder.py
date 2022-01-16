"""
Created on Jan 11, 2022
@author: AC

This module provides the streamlit UI to build your customized portfolio.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

import streamlit as st

from quantfin.market.assets import AssetClasses, Indexes
from quantfin.portfolio_selection.strategies import PortfolioStrategies
from quantfin.portfolio_selection.portfolio_optimization.objective_functions import (
    ObjectiveFunctions,
)

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

    asset_classes = st.multiselect(
        label="Choose the asset classes you are interested in",
        default=AssetClasses.STOCKS.value,
        options=AssetClasses.list(),
    )
    if AssetClasses.STOCKS.value in asset_classes:
        reference_index = st.selectbox(
            label="Enter a reference index for stocks", options=Indexes.list()
        )
    ptf_strategy = st.selectbox(
        label="Enter a portfolio selection strategy",
        options=PortfolioStrategies.list(),
    )

    # SIDEBAR (PARAMETERS):

    st.sidebar.title("Parameters")

    start_date = st.sidebar.date_input(
        label="Provide a starting date for the learning period",
        value=datetime.today() - relativedelta(years=3),
    )
    end_date = st.sidebar.date_input(
        label="Provide the end date for the learning period",
        value=datetime.today(),
    )

    if ptf_strategy == "Portfolio Optimization":
        objective_functions = st.multiselect(
            label="Choose the optimization model",
            default=ObjectiveFunctions.VARIANCE.value,
            options=ObjectiveFunctions.list(),
        )
        # min_max = st.radio(
        #     label="Choose wether to minimize or maximize the objective function",
        #     options=("Min", "Max"),
        # )
        with st.expander("See explanation"):
            if ObjectiveFunctions.VARIANCE.value in objective_functions:
                st.write(
                    """
                The Portfolio Variance measures the squared distance of portfolio returns from the mean.
            """
                )
        if len(objective_functions) > 1:
            weights_objectives = {}
            for obj_fun in objective_functions:
                weights_objectives[obj_fun] = st.sidebar.number_input(
                    label=f"Choose the weight for {obj_fun}",
                    min_value=0.0,
                    max_value=1.0,
                    value=1 / len(objective_functions),
                )
        risk_appetite = st.sidebar.number_input(
            label="Choose a level of risk appetite", min_value=0.0, max_value=1.0
        )
        constraints = st.sidebar.multiselect(
            label="Choose the constraints you prefer",
            default=("Budget", "Long-only"),
            options=("Budget", "Long-only", "Max Instrument Weight"),
        )
        if "Max Instrument Weight" in constraints:
            _for_all_assets = st.sidebar.checkbox(
                label="Apply to all assets", value=True
            )
            if _for_all_assets:
                max_weight_for_all_assets = st.sidebar.number_input(
                    label="Choose a maximum weight",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                )
            else:
                raise NotImplementedError
    else:
        raise NotImplementedError

    st.write(
        """
             ## Allocation
             
             Here you can see the asset allocation:
             """
    )

    st.write(
        """
             # Backtester
             
             Please choose a period and a rebalance frequency to backtest your portfolio.  
             #TODO: Compare multiple strategies.
             """
    )
