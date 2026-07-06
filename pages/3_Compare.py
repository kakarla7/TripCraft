import streamlit as st
from utils.supabase_client import get_user_searches, get_search_by_slug
from utils.auth import get_current_user, require_login

st.set_page_config(page_title="TripCraft — Compare", page_icon="✈️", layout="wide")

st.markdown("### ⚖️ Compare two trip searches")
st.markdown("Pick two of your saved searches to compare side by side.")
st.divider()

if not require_login("Sign in to access your saved searches for comparison."):
    st.stop()

user = get_current_user()

# Load user's saved searches
try:
    searches = get_user_searches(user["id"])
except Exception as e:
    st.error(f"Could not load your searches: {e}")
    st.stop()

if len(searches) < 2:
    st.info("You need at least 2 saved searches to compare. Run a search and save it first.")
    if st.button("← Go to search"):
        st.switch_page("pages/1_Search.py")
    st.stop()

# Format search options for dropdown
def format_search(s):
    p = s.get("search_params", {})
    return f"{p.get('origin','?')} → ? · {p.get('month','?')} · {p.get('days','?')} days"

options = {format_search(s): s for s in searches}
option_labels = list(options.keys())

col1, col2 = st.columns(2)
with col1:
    choice_a = st.selectbox("First search", option_labels, key="compare_a")
with col2:
    remaining = [o for o in option_labels if o != choice_a]
    choice_b = st.selectbox("Second search", remaining, key="compare_b")

st.markdown("")

if st.button("Compare →", type="primary"):
    search_a = options[choice_a]
    search_b = options[choice_b]
    cards_a = search_a.get("results", [])
    cards_b = search_b.get("results", [])
    params_a = search_a.get("search_params", {})
    params_b = search_b.get("search_params", {})

    st.divider()

    # Side by side best match from each search
    col_a, col_mid, col_b = st.columns([5, 1, 5])

    with col_a:
        st.markdown(f"**Search A:** {params_a.get('origin','?')} · "
                    f"{params_a.get('month','?')} · {params_a.get('days','?')} days")
        st.markdown(f"Interests: {', '.join(params_a.get('interests', []))}")
        st.markdown("")
        for card in cards_a:
            with st.expander(f"{'⭐ ' if card.get('is_best_match') else ''}{card['name']}, {card['state']}"):
                st.markdown(f"*{card.get('why','')}*")
                st.markdown(f"🌤 {card.get('weather_summary','')}")
                st.markdown(f"✈️ Flight: ${card.get('flight_low',0)}–${card.get('flight_high',0)}")
                st.markdown(f"💰 Total: ${card.get('total_low',0)}–${card.get('total_high',0)}")

    with col_mid:
        st.markdown("<div style='text-align:center; padding-top:80px; font-size:24px;'>vs</div>",
                    unsafe_allow_html=True)

    with col_b:
        st.markdown(f"**Search B:** {params_b.get('origin','?')} · "
                    f"{params_b.get('month','?')} · {params_b.get('days','?')} days")
        st.markdown(f"Interests: {', '.join(params_b.get('interests', []))}")
        st.markdown("")
        for card in cards_b:
            with st.expander(f"{'⭐ ' if card.get('is_best_match') else ''}{card['name']}, {card['state']}"):
                st.markdown(f"*{card.get('why','')}*")
                st.markdown(f"🌤 {card.get('weather_summary','')}")
                st.markdown(f"✈️ Flight: ${card.get('flight_low',0)}–${card.get('flight_high',0)}")
                st.markdown(f"💰 Total: ${card.get('total_low',0)}–${card.get('total_high',0)}")
