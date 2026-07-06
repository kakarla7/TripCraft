import streamlit as st
from utils.auth import get_current_user, require_login
from utils.supabase_client import get_user_searches, get_user_trips
from utils.share import get_share_url, render_share_sheet

st.set_page_config(page_title="TripCraft — My Trips", page_icon="✈️", layout="wide")

st.markdown("### 🗺️ My trips")
st.divider()

if not require_login("Sign in to see your saved searches and trips."):
    st.stop()

user = get_current_user()
st.markdown(f"Welcome back, **{user['name'].split()[0]}**!")
st.markdown("")

# ── Saved searches ─────────────────────────────────────────────────────────
st.markdown("#### Saved searches")

try:
    searches = get_user_searches(user["id"])
except Exception as e:
    searches = []
    st.warning(f"Could not load searches: {e}")

if not searches:
    st.info("No saved searches yet. Run a search and save it!")
    if st.button("Start searching →", type="primary"):
        st.switch_page("pages/1_Search.py")
else:
    for s in searches:
        p = s.get("search_params", {})
        cards = s.get("results", [])
        slug = s.get("share_slug", "")

        with st.expander(
            f"📍 {p.get('origin','?')} → {p.get('month','?')} · "
            f"{p.get('days','?')} days · {len(cards)} destinations"
        ):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.markdown(f"**Interests:** {', '.join(p.get('interests', []))}")
                st.markdown(f"**Travelling:** {', '.join(p.get('travellers', []))}")
                st.markdown("**Top match:** "
                            + next((c['name'] for c in cards if c.get('is_best_match')),
                                   cards[0]['name'] if cards else '—'))
            with cols[1]:
                if st.button("View results", key=f"view_{slug}"):
                    st.session_state["results"] = cards
                    st.session_state["search_params"] = p
                    st.switch_page("pages/2_Results.py")
            with cols[2]:
                share_url = get_share_url(slug, "results")
                if st.button("Share", key=f"share_{slug}"):
                    st.session_state[f"show_share_{slug}"] = True

            if st.session_state.get(f"show_share_{slug}"):
                render_share_sheet(share_url)

# ── Saved trip plans (Phase 2) ─────────────────────────────────────────────
st.markdown("")
st.markdown("#### Full trip plans")

try:
    trips = get_user_trips(user["id"])
except Exception as e:
    trips = []

if not trips:
    st.info("No full trip plans yet. Plans will appear here once Phase 2 is live.")
else:
    for trip in trips:
        with st.expander(f"✈️ {trip['destination']}"):
            st.json(trip.get("full_plan", {}))
