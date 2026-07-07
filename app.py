from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="TripCraft — AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar and default menu
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

from utils.auth import is_logged_in, render_nav_auth

# ── Nav ───────────────────────────────────────────────────────────────────────
col_logo, col_mid, col_auth = st.columns([2, 4, 2])
with col_logo:
    st.markdown("### ✈️ TripCraft")
with col_mid:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Search", use_container_width=True):
            st.switch_page("pages/1_Search.py")
    with c2:
        if st.button("My Trips", use_container_width=True):
            st.switch_page("pages/4_My_Trips.py")
    with c3:
        bucket = st.session_state.get("compare_bucket", [])
        label = f"Compare ({len(bucket)})" if bucket else "Compare"
        if st.button(label, use_container_width=True):
            st.switch_page("pages/3_Compare.py")
with col_auth:
    render_nav_auth()

st.divider()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 1rem 2rem;">
    <div style="font-size:48px; margin-bottom:1rem;">✈️</div>
    <h1 style="font-size:2.5rem; font-weight:600; color:#1A1A1A; margin-bottom:0.5rem;">
        Where should you go next?
    </h1>
    <p style="font-size:1.1rem; color:#666; max-width:480px; margin:0 auto 2rem;">
        TripCraft uses AI to find your perfect US destination — 
        matched to your interests, budget, and travel style.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Plan my trip →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Search.py")

st.markdown("")

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin: 2rem 0 1rem;">
    <h2 style="font-size:1.4rem; font-weight:500; color:#1A1A1A;">How it works</h2>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
steps = [
    ("🏙️", "Tell us about your trip", "Starting city, month, days, and interests"),
    ("🤖", "AI finds your matches", "4 agents search destinations, weather, and costs in parallel"),
    ("🗺️", "Compare destinations", "Side-by-side comparison of up to 4 destinations"),
    ("💾", "Save and share", "Save your searches and share with friends via link or AirDrop"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4], steps):
    with col:
        st.markdown(f"""
        <div style="text-align:center; padding:1.25rem; background:#F5F5F0;
            border-radius:12px; height:160px;">
            <div style="font-size:28px; margin-bottom:8px;">{icon}</div>
            <div style="font-weight:500; font-size:14px; color:#1A1A1A;
                margin-bottom:6px;">{title}</div>
            <div style="font-size:12px; color:#666; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#F5F5F0; border-radius:12px; padding:1.5rem; margin:1rem 0;">
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; text-align:center; gap:1rem;">
        <div>
            <div style="font-size:1.8rem; font-weight:600; color:#D85A30;">100+</div>
            <div style="font-size:13px; color:#666;">US destinations</div>
        </div>
        <div>
            <div style="font-size:1.8rem; font-weight:600; color:#D85A30;">4</div>
            <div style="font-size:13px; color:#666;">AI agents working in parallel</div>
        </div>
        <div>
            <div style="font-size:1.8rem; font-weight:600; color:#D85A30;">Free</div>
            <div style="font-size:13px; color:#666;">No credit card needed</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Get started →", type="primary", use_container_width=True, key="cta2"):
        st.switch_page("pages/1_Search.py")