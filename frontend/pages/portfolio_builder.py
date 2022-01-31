"""
Created on Jan 11, 2022
@author: AC

This module provides the streamlit UI to build your customized portfolio.
"""
from datetime import date
from typing import Optional
from dateutil.relativedelta import relativedelta
import pandas as pd

import plotly.graph_objects as go
import streamlit as st

from quantfin.market.investment_universe import (
    InvestmentUniverse,
    MarketIndex,
    PriceType,
)
from quantfin.market.assets import AssetClasses
from quantfin.portfolio_selection.strategies import PortfolioStrategies
from quantfin.portfolio_selection.portfolio_optimization import (
    ConstraintType,
    ObjectiveType,
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

            objective_function = st.multiselect(
                label="Choose the optimization model",
                default=ObjectiveType.VARIANCE.value,
                options=ObjectiveType.list(),
            )
            risk_appetite = st.sidebar.number_input(
                label="Choose a level of risk appetite", min_value=0.0, max_value=1.0
            )
            constraints = st.sidebar.multiselect(
                label="Choose the constraints you prefer",
                default=ConstraintType.NO_SHORTSELLING.value,
                options=ConstraintType.list(),
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
            regularization_weight = st.sidebar.number_input(
                label="Choose a level of regularization",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
            )
            with st.expander("See explanation"):
                if ObjectiveType.VARIANCE.value in objective_function:
                    st.write(
                        """
                    The Portfolio Variance measures the squared distance of portfolio returns from the mean.
                """
                    )
                if ObjectiveType.MAD.value in objective_function:
                    st.write(
                        """
                    The Portfolio MAD measures the absolute deviation of portfolio returns from the mean.
                """
                    )
                if ObjectiveType.CVAR.value in objective_function:
                    st.write(
                        """
                    The Portfolio Conditional Value-at-Risk measures the expected portfolio loss at a certain confidence level.
                """
                    )
            if len(objective_function) > 1:
                weights_objectives = {}
                for obj_fun in objective_function:
                    weights_objectives[obj_fun] = st.sidebar.number_input(
                        label=f"Choose the weight for {obj_fun}",
                        min_value=0.0,
                        max_value=1.0,
                        value=1 / len(objective_function),
                    )

            opt_problem = OptimizationProblem(
                returns=univ.prices.pct_change().dropna(),
                objective_type=ObjectiveType(objective_function[0]),
                constraints=[ConstraintType(constraint) for constraint in constraints],
                regularization_weight=regularization_weight,
            )
            opt_ptf = opt_problem.solve()

    st.write(
        """
             ## Allocation
             
             Here you can see the asset allocation:
             """
    )
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[str(key) for key in opt_ptf.nonzero_holdings.keys()],
            y=list(opt_ptf.nonzero_holdings.values()),
        )
    )
    st.plotly_chart(fig)
    # allocation = plt.bar(
    #     [str(key) for key in opt_ptf.nonzero_holdings.keys()],
    #     opt_ptf.nonzero_holdings.values(),
    # )
    # st.pyplot(fig=allocation)
    # st.bar_chart(
    #     data=pd.DataFrame(
    #         opt_ptf.nonzero_holdings,
    #         index=[1],
    #         columns=[str(key) for key in opt_ptf.nonzero_holdings.keys()],
    #     )
    # )

    st.write(
        """
             # Backtester
             
             Please choose a period and a rebalance frequency to backtest your portfolio.  
             #TODO: Compare multiple strategies.
             """
    )
