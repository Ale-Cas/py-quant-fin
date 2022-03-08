"""
Created on Jan 11, 2022
@author: AC

This module provides the streamlit UI to build your customized portfolio.
"""
from datetime import date
from typing import Optional
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from quantfin.market.investment_universe import (
    InvestmentUniverse,
    MarketIndex,
    PriceType,
)
from quantfin.market.assets import AssetClasses
from quantfin.portfolio_selection.strategy import PortfolioStrategies
from quantfin.portfolio_selection.portfolio_optimization import (
    Constraint,
    OptimizationModel,
    OptimizationProblem,
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

    # SIDEBAR (PARAMETERS):

    st.sidebar.title("Parameters")
    start_date = st.sidebar.date_input(
        label="Provide a starting date for the learning period",
        value=date.today() - relativedelta(years=3),
    )
    end_date = st.sidebar.date_input(
        label="Provide the end date for the learning period",
        value=date.today(),
    )
    prices_column = st.sidebar.selectbox(
        label="Enter a type of price",
        options=PriceType.list(),
    )

    # INPUTs:

    col1, col2 = st.columns(2)

    with col1:
        asset_classes = st.multiselect(
            label="Choose the asset classes you are interested in",
            default=AssetClasses.STOCKS.value,
            options=AssetClasses.list(),
        )
        if AssetClasses.STOCKS.value in asset_classes:
            use_index = st.checkbox(
                label="Do you want to use a reference index as investment universe?",
                value=True,
            )
            if use_index:
                reference_index = st.selectbox(
                    label="Choose a reference index for stocks",
                    options=MarketIndex.list(),
                    index=1,
                )
                univ = InvestmentUniverse(reference_index=reference_index)
            else:
                univ = InvestmentUniverse()
        else:
            NotImplemented

    @st.cache(persist=True)
    def get_univ_prices(
        universe: InvestmentUniverse,
        price_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> pd.DataFrame:
        return universe.get_prices(
            prices_column=price_type, start=start_date, end=end_date
        )

    with st.spinner("Getting prices..."):
        univ.prices = get_univ_prices(
            universe=univ,
            price_type=prices_column,
            start_date=start_date,
            end_date=end_date,
        )
    with col2:

        ptf_strategy = st.selectbox(
            label="Enter a portfolio selection strategy",
            options=PortfolioStrategies.list(),
        )
        if ptf_strategy == "Portfolio Optimization":

            subcls = {cls.__name__: cls for cls in OptimizationModel.__subclasses__()}
            optimization_model = st.selectbox(
                label="Choose the optimization model",
                options=list(subcls.keys()),
            )
            # risk_appetite = st.sidebar.number_input(
            #     label="Choose a level of risk appetite", min_value=0.0, max_value=1.0
            # )
            constraints = st.sidebar.multiselect(
                label="Choose the constraints you prefer",
                default=Constraint.NO_SHORTSELLING.value,
                options=Constraint.list(),
            )

            model = subcls[optimization_model]
            opt_model = model(
                constraints={Constraint(constraint) for constraint in constraints}
            )
            opt_problem = OptimizationProblem(
                optimization_model=opt_model, investment_universe=univ
            )
            with st.expander("See model explanation"):
                if optimization_model == "MeanVariance":
                    st.write(
                        """
                    The Mean-Variance model was developed by Harry Markovitz in 1952-1959. 
                    It finds an optimal portfolio according to trade-off between the expected return
                    and the variance. 
                    The Portfolio Variance measures the squared distance of portfolio returns from the mean.
                    """
                    )
                if optimization_model == "MeanMAD":
                    st.write(
                        """
                    The Mean-MAD model was developed by Young. 
                    It finds an optimal portfolio according to trade-off between the expected return
                    and the Mean Absolute Deviation (MAD). 
                    The Portfolio MAD measures the absolute deviation of portfolio returns from the mean.
                    """
                    )
                if optimization_model == "MeanCVaR":
                    st.write(
                        """
                    The Mean-CVaR model was developed by Uryasev and Checklov. 
                    It finds an optimal portfolio according to trade-off between the expected return
                    and the Conditional Value-at-Risk (CVaR). 
                    The Portfolio CVaR measures the expected portfolio loss at a certain confidence level.
                    """
                    )
            opt_ptf = opt_problem.solve()
        else:
            raise NotImplementedError

    st.write(
        """
             ## Allocation
             
             Here you can see the asset allocation:
             """
    )

    bar_chart = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Assets": [
                        str(stock.ticker) for stock in opt_ptf.nonzero_holdings.keys()
                    ],
                    "Weights": opt_ptf.nonzero_holdings.values(),
                }
            )
        )
        .mark_bar()
        .encode(x="Assets", y="Weights")
    )
    st.altair_chart(bar_chart, use_container_width=True)

    st.write(
        """
             # Backtester
             
             Please choose a period and a rebalance frequency to backtest your portfolio.  
             #TODO: Compare multiple strategies.
             """
    )
