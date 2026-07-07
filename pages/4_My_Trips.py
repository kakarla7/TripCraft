from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="TripCraft — My Trips", page_icon="✈️", layout="wide")

from utils.auth import get_current_user, is_logged_in, render_nav_auth, render_auth_page
from utils.supabase_client import get_user_searches, get_user_trips, delete_search
from utils.share import get_share_url, render_share_sheet

# ── Nav ───────────────────────────────────────────────────────────────────────
col_logo, col_search, col_trips, col_compare, col_auth = st.columns([2, 1, 1, 1, 2])
with col_logo:
    if st.button("✈️ TripCraft", key="logo"):
        st.switch_page("app.py")
with col_search:
    if st.button("Search", use_container_width=True):
        st.switch_page("pages/1_Search.py")
with col_trips:
    st.button("My Trips", use_container_width=True, disabled=True)
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
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem;">
        <div style="font-size:48px; margin-bottom:1rem;">🔐</div>
        <h2 style="font-size:1.4rem; font-weight:500; color:#1A1A1A; margin-bottom:0.5rem;">
            Sign in to see your trips
        </h2>
        <p style="color:#666; margin-bottom:1.5rem;">
            Save searches, compare destinations, and share trips with friends.
        </p>
    </div>
    """, unsafe_allow_html=True)
    render_auth_page()
    st.stop()

user = get_current_user()

# ── Profile header ────────────────────────────────────────────────────────────
col_info, col_stats = st.columns([2, 3])
with col_info:
    st.markdown(f"## 👤 {user.get('name', 'Traveller')}")
    st.markdown(f"📧 {user.get('email', '')}")

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
        st.metric("In compare", len(st.session_state.get("compare_bucket", [])))

st.divider()

# ── Saved searches ────────────────────────────────────────────────────────────
st.markdown("### 🔍 Saved searches")

if not searches:
    st.markdown("""
    <div style="text-align:center; padding:2.5rem; background:#F5F5F0;
        border-radius:12px; margin:1rem 0;">
        <div style="font-size:36px; margin-bottom:0.75rem;">🗺️</div>
        <div style="font-weight:500; font-size:15px; color:#1A1A1A;
            margin-bottom:0.5rem;">No saved searches yet</div>
        <div style="font-size:13px; color:#666;">
            Run a search and click "Save & Share" to save it here.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start searching →", type="primary"):
        st.switch_page("pages/1_Search.py")
else:
    for s in searches:
        p = s.get("search_params", {})
        results = s.get("results", [])
        slug = s.get("share_slug", "")
        sname = s.get("name", "Unnamed search")

        with st.expander(
            f"📍 {sname} · {p.get('origin','?')} → "
            f"{p.get('month','?')} · {p.get('days','?')} days"
        ):
            st.markdown(f"**Interests:** {', '.join(p.get('interests', []))}")
            st.markdown(f"**Travelling:** {', '.join(p.get('travellers', []))}")
            best = next(
                (c["name"] for c in results if c.get("is_best_match")),
                results[0]["name"] if results else "—"
            )
            st.markdown(f"**Best match:** {best}")
            st.markdown(f"**All destinations:** {', '.join(c['name'] for c in results)}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("View results", key=f"view_{slug}", use_container_width=True):
                    st.session_state["results"] = results
                    st.session_state["search_params"] = p
                    st.switch_page("pages/2_Results.py")
            with c2:
                if st.button("Add to compare", key=f"compare_{slug}", use_container_width=True):
                    if "compare_bucket" not in st.session_state:
                        st.session_state.compare_bucket = []
                    for dest in results:
                        if len(st.session_state.compare_bucket) < 4:
                            if not any(b["name"] == dest["name"]
                                       for b in st.session_state.compare_bucket):
                                st.session_state.compare_bucket.append({
                                    **dest,
                                    "search_name": sname,
                                    "search_params": p
                                })
                    st.success("Added to compare!")
                    st.rerun()
            with c3:
                if st.button("Share", key=f"share_{slug}", use_container_width=True):
                    st.session_state[f"show_share_{slug}"] = (
                        not st.session_state.get(f"show_share_{slug}", False)
                    )
                    st.rerun()
            with c4:
                if st.button("🗑 Delete", key=f"delete_{slug}", use_container_width=True):
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
    st.markdown("""
    <div style="text-align:center; padding:2rem; background:#F5F5F0;
        border-radius:12px; margin:0.5rem 0;">
        <div style="font-size:32px; margin-bottom:0.75rem;">🏗️</div>
        <div style="font-weight:500; font-size:14px; color:#1A1A1A;
            margin-bottom:0.4rem;">Coming in Phase 2</div>
        <div style="font-size:12px; color:#666;">
            Full day-by-day itineraries, hotel recommendations, 
            and budget breakdowns will appear here.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for trip in trips:
        with st.expander(f"✈️ {trip['destination']}"):
            st.json(trip.get("full_plan", {}))