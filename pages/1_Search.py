from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="TripCraft — Find your trip",
    page_icon="✈️",
    layout="wide"
)

import asyncio
from agents import destination_agent, weather_agent, budget_agent, comparator_agent
from utils.auth import render_nav_auth
from utils.cities import US_CITIES
from utils.mobile import inject_mobile_css

inject_mobile_css()

# ── Nav ───────────────────────────────────────────────────────────────────────
col_logo, col_search, col_trips, col_compare, col_auth = st.columns([2, 1, 1, 1, 2])
with col_logo:
    if st.button("✈️ TripCraft", key="logo"):
        st.switch_page("app.py")
with col_search:
    st.button("Search", use_container_width=True, disabled=True)
with col_trips:
    if st.button("My Trips", use_container_width=True):
        st.switch_page("pages/4_My_Trips.py")
with col_compare:
    bucket = st.session_state.get("compare_bucket", [])
    label = f"Compare ({len(bucket)})" if bucket else "Compare"
    if st.button(label, use_container_width=True):
        st.switch_page("pages/3_Compare.py")
with col_auth:
    render_nav_auth()

st.divider()

st.markdown("## Where should you go?")
st.markdown("Tell us about your trip and we'll find the best US destinations for you.")
st.markdown("")

# ── Trip details ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    origin = st.selectbox(
        "Starting city",
        options=[""] + US_CITIES,
        index=0,
        help="Type to filter cities"
    )
with col2:
    month = st.selectbox("Month of travel", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ], index=9)
with col3:
    days = st.number_input("Number of days", min_value=2, max_value=30, value=7)

# ── Interest tags — mobile friendly buttons ───────────────────────────────────
st.markdown("**What are you into?**")

INTERESTS = [
    "National Parks", "Hiking", "Historic places", "Museums",
    "Food scene", "Beach", "Nightlife", "Shopping",
    "Adventure", "Romantic getaway"
]
TRAVELLER_TYPES = ["Kid friendly", "Senior friendly", "Solo", "Couple", "Group"]

if "selected_interests" not in st.session_state:
    st.session_state.selected_interests = []
if "selected_travellers" not in st.session_state:
    st.session_state.selected_travellers = []

# Interest buttons — 5 per row
int_cols = st.columns(5)
for i, interest in enumerate(INTERESTS):
    with int_cols[i % 5]:
        is_on = interest in st.session_state.selected_interests
        label = f"✓ {interest}" if is_on else interest
        if st.button(
            label,
            key=f"int_{interest}",
            use_container_width=True,
            type="primary" if is_on else "secondary"
        ):
            if interest in st.session_state.selected_interests:
                st.session_state.selected_interests.remove(interest)
            else:
                st.session_state.selected_interests.append(interest)
            st.rerun()

st.markdown("**Who's travelling?**")

# Traveller buttons
trav_cols = st.columns(5)
for i, ttype in enumerate(TRAVELLER_TYPES):
    with trav_cols[i % 5]:
        is_on = ttype in st.session_state.selected_travellers
        label = f"✓ {ttype}" if is_on else ttype
        if st.button(
            label,
            key=f"tt_{ttype}",
            use_container_width=True,
            type="primary" if is_on else "secondary"
        ):
            if ttype in st.session_state.selected_travellers:
                st.session_state.selected_travellers.remove(ttype)
            else:
                st.session_state.selected_travellers.append(ttype)
            st.rerun()

st.markdown("**When are you booking?**")
booking_window = st.radio(
    "Booking window",
    options=["3_months", "4_8_weeks", "last_minute"],
    format_func=lambda x: {
        "3_months": "3+ months out (best prices)",
        "4_8_weeks": "4–8 weeks out",
        "last_minute": "Under 2 weeks (last minute)"
    }[x],
    horizontal=True,
    label_visibility="collapsed"
)

# Show selected summary
selected = st.session_state.selected_interests + st.session_state.selected_travellers
if selected:
    st.caption(f"Selected: {', '.join(selected)}")

st.markdown("")
search_clicked = st.button(
    "Find my destinations →",
    type="primary",
    use_container_width=True
)

# ── Run agents ────────────────────────────────────────────────────────────────
if search_clicked:
    if not origin:
        st.warning("Please select your starting city.")
        st.stop()

    interests = st.session_state.selected_interests
    travellers = st.session_state.selected_travellers

    st.markdown("")
    progress = st.progress(0)
    status = st.empty()

    async def run_all():
        status.markdown("🔍 **Finding best destinations for you...**")
        progress.progress(20)
        destinations = await destination_agent.run(
            origin, month, days, interests, travellers
        )

        status.markdown("🌤 **Checking weather and 💰 estimating costs...**")
        progress.progress(50)
        weather_data, budget_data = await asyncio.gather(
            weather_agent.run(destinations, month),
            budget_agent.run(origin, destinations, days, booking_window)
        )

        status.markdown("⭐ **Ranking your matches...**")
        progress.progress(80)
        cards = await comparator_agent.run(
            destinations, weather_data, budget_data, interests, travellers
        )

        progress.progress(100)
        status.markdown("✅ **Done! Here are your destinations.**")
        return cards

    try:
        cards = asyncio.run(run_all())
        st.session_state["results"] = cards
        st.session_state["search_params"] = {
            "origin": origin,
            "month": month,
            "days": days,
            "interests": interests,
            "travellers": travellers,
            "booking_window": booking_window
        }
        st.switch_page("pages/2_Results.py")
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.exception(e)