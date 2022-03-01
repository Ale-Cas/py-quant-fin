"""
This file generates the homepage.
"""
import streamlit as st

from frontend.pages import dashboard, portfolio_builder
from multipage import MultiPage

if __name__ == "__main__":
    app = MultiPage()
    st.set_page_config(
        page_title="Quant Finance",
        layout="wide",
        page_icon="📈",
        initial_sidebar_state="collapsed",
    )
    st.title("Homepage")

    app.add_page(dashboard.title, dashboard.app)
    app.add_page(portfolio_builder.title, portfolio_builder.app)

    app.run()
