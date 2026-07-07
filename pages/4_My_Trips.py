from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="TripCraft — My Trips", page_icon="✈️", layout="wide")

from utils.auth import get_current_user, is_logged_in, render_nav_auth, render_auth_page
from utils.supabase_client import get_user_searches, get_user_trips, delete_search
from utils.share import get_share_url, render_share_sheet

# ── Nav ───────────────────────────────────────────────────────────────────────
col_logo, col_search, col_trips, col_compare, col_auth = st.columns([2, 1, 1, 1, 2])
with col_logo:
    st.markdown("### ✈️ TripCraft")
with col_search:
    if st.button("Search", use_container_width=True):
        st.switch_page("pages/1_Search.py")
with col_trips:
    st.button("My trips", use_container_width=True, disabled=True)
with col_compare:
    bucket = st.session_state.get("compare_bucket", [])
    label = f"Compare ({len(bucket)})" if bucket else "Compare"
    if st.button(label, use_container_width=True):
        st.switch_page("pages/3_Compare.py")
with col_auth:
    render_nav_auth()

st.divider()

# ── Require login ─────────────────────────────────────────────────────────────
if not is_logged_in():
    render_auth_page()
    st.stop()

user = get_current_user()
name = user.get("name", "Traveller").split()[0]

# ── Profile header ────────────────────────────────────────────────────────────
col_info, col_stats = st.columns([2, 3])
with col_info:
    st.markdown(f"## 👤 {user.get('name', 'Traveller')}")
    st.markdown(f"📧 {user.get('email', '')}")

# Load data
try:
    searches = get_user_searches(user["id"])
except Exception:
    searches = []

try:
    trips = get_user_trips(user["id"])
except Exception:
    trips = []

with col_stats:
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Saved searches", len(searches))
    with s2:
        st.metric("Trip plans", len(trips))
    with s3:
        bucket = st.session_state.get("compare_bucket", [])
        st.metric("In compare", len(bucket))

st.divider()

# ── Saved searches ────────────────────────────────────────────────────────────
st.markdown("### 🔍 Saved searches")

if not searches:
    st.info("No saved searches yet. Run a search and save it!")
    if st.button("Start searching →", type="primary"):
        st.switch_page("pages/1_Search.py")
else:
    for s in searches:
        p = s.get("search_params", {})
        results = s.get("results", [])
        slug = s.get("share_slug", "")
        sname = s.get("name", "Unnamed search")

        with st.expander(f"📍 {sname} · {p.get('origin','?')} → {p.get('month','?')} · {p.get('days','?')} days"):
            st.markdown(f"**Interests:** {', '.join(p.get('interests', []))}")
            st.markdown(f"**Travelling:** {', '.join(p.get('travellers', []))}")

            best = next((c["name"] for c in results if c.get("is_best_match")),
                        results[0]["name"] if results else "—")
            st.markdown(f"**Best match:** {best}")
            st.markdown(f"**Destinations:** {', '.join(c['name'] for c in results)}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("View results", key=f"view_{slug}", use_container_width=True):
                    st.session_state["results"] = results
                    st.session_state["search_params"] = p
                    st.switch_page("pages/2_Results.py")
            with c2:
                bucket = st.session_state.get("compare_bucket", [])
                if st.button("Add to compare", key=f"compare_{slug}", use_container_width=True):
                    for dest in results:
                        if len(st.session_state.get("compare_bucket", [])) < 4:
                            if not any(b["name"] == dest["name"]
                                       for b in st.session_state.get("compare_bucket", [])):
                                if "compare_bucket" not in st.session_state:
                                    st.session_state.compare_bucket = []
                                st.session_state.compare_bucket.append({
                                    **dest,
                                    "search_name": sname,
                                    "search_params": p
                                })
                    st.success("Added to compare!")
                    st.rerun()
            with c3:
                if st.button("Share", key=f"share_{slug}", use_container_width=True):
                    st.session_state[f"show_share_{slug}"] = True
            with c4:
                if st.button("Delete", key=f"delete_{slug}", use_container_width=True):
                    try:
                        delete_search(s["id"], user["id"])
                        st.success("Deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not delete: {e}")

            if st.session_state.get(f"show_share_{slug}"):
                share_url = get_share_url(slug, "Results")
                render_share_sheet(share_url)

# ── Trip plans (Phase 2) ──────────────────────────────────────────────────────
st.markdown("")
st.markdown("### ✈️ Full trip plans")

if not trips:
    st.info("Full trip plans will appear here once Phase 2 is live.")
else:
    for trip in trips:
        with st.expander(f"✈️ {trip['destination']}"):
            st.json(trip.get("full_plan", {}))