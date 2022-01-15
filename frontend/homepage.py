"""
This file generates the homepage.
"""
import streamlit as st

from frontend.pages import data_visualizer, portfolio_builder
from multipage import MultiPage


app = MultiPage()
st.set_page_config(
    page_title="Quant Finance",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed",
)
st.title("Homepage")

app.add_page(data_visualizer.title, data_visualizer.app)
app.add_page(portfolio_builder.title, portfolio_builder.app)

app.run()
