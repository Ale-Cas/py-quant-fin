"""
This file generates the homepage.
"""
import streamlit as st

from frontend.pages import stock_data
from multipage import MultiPage

app = MultiPage()
st.set_page_config(page_title="Homepage", layout="wide")
st.title("Homepage")

app.add_page(stock_data.title, stock_data.app)

app.run()
