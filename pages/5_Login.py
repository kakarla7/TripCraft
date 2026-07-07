from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="TripCraft — Login", page_icon="✈️", layout="wide")

from utils.auth import render_auth_page, is_logged_in

if is_logged_in():
    st.switch_page("pages/1_Search.py")

render_auth_page()