from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="TripCraft — Results", page_icon="✈️", layout="wide")

from utils.auth import get_current_user, is_logged_in, require_login, render_nav_auth
from utils.mobile import inject_mobile_css

inject_mobile_css()
from utils.share import generate_slug, get_share_url, render_share_sheet
from utils.supabase_client import save_search, get_search_by_slug

# ── Nav ───────────────────────────────────────────────────────────────────────
col_logo, col_search, col_trips, col_compare, col_auth = st.columns([2, 1, 1, 1, 2])
with col_logo:
    st.markdown("### ✈️ TripCraft")
with col_search:
    if st.button("Search", use_container_width=True):
        st.switch_page("pages/1_Search.py")
with col_trips:
    if st.button("My trips", use_container_width=True):
        st.switch_page("pages/4_My_Trips.py")
with col_compare:
    bucket = st.session_state.get("compare_bucket", [])
    label = f"Compare ({len(bucket)})" if bucket else "Compare"
    if st.button(label, use_container_width=True):
        st.switch_page("pages/3_Compare.py")
with col_auth:
    render_nav_auth()

st.divider()

# ── Load results ──────────────────────────────────────────────────────────────
cards = None
search_params = None
share_slug = st.query_params.get("s", None)

if share_slug:
    try:
        saved = get_search_by_slug(share_slug)
        if saved:
            cards = saved["results"]
            search_params = saved["search_params"]
            st.info("👀 You're viewing a shared TripCraft search.")
    except Exception:
        st.error("This share link has expired or doesn't exist.")
        st.stop()
else:
    cards = st.session_state.get("results")
    search_params = st.session_state.get("search_params")

if not cards:
    st.warning("No results found. Please run a search first.")
    if st.button("← Back to search"):
        st.switch_page("pages/1_Search.py")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
p = search_params or {}
col_back, col_title = st.columns([1, 5])
with col_back:
    if st.button("← New search"):
        st.switch_page("pages/1_Search.py")
with col_title:
    st.markdown(
        f"### {len(cards)} destinations matched · "
        f"{p.get('month','?')} · {p.get('days','?')} days · "
        f"from {p.get('origin','?')}"
    )

st.divider()

# ── Save + Share ──────────────────────────────────────────────────────────────
if "current_share_slug" not in st.session_state:
    col_name, col_save = st.columns([3, 1])
    with col_name:
        trip_name = st.text_input(
            "Name this search",
            placeholder="e.g. Family October trip",
            key="trip_name_input"
        )
    with col_save:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save & Share", type="primary"):
            if not is_logged_in():
                st.warning("🔐 Sign in first to save. Go to My Trips to sign in.")
            else:
                user = get_current_user()
                name = trip_name.strip() or f"{p.get('origin','Trip')} · {p.get('month','')}"
                slug = generate_slug()
                try:
                    save_search(user["id"], name, search_params, cards, slug)
                    st.session_state["current_share_slug"] = slug
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save: {e}")
else:
    slug = st.session_state["current_share_slug"]
    share_url = get_share_url(slug, "Results")
    st.success("✅ Saved!")
    render_share_sheet(share_url)

st.markdown("")

# ── Destination cards ─────────────────────────────────────────────────────────
INTEREST_COLORS = {
    "National Parks": ("#E1F5EE", "#0F6E56"),
    "Hiking": ("#EAF3DE", "#3B6D11"),
    "Food scene": ("#FAEEDA", "#854F0B"),
    "Historic places": ("#EEEDFE", "#534AB7"),
    "Museums": ("#EEEDFE", "#534AB7"),
    "Beach": ("#E6F1FB", "#185FA5"),
    "Nightlife": ("#FBEAF0", "#72243E"),
    "Shopping": ("#F1EFE8", "#444441"),
    "Adventure": ("#FAECE7", "#712B13"),
    "Romantic getaway": ("#FBEAF0", "#72243E"),
    "Kid friendly": ("#FAECE7", "#993C1D"),
    "Senior friendly": ("#E6F1FB", "#185FA5"),
    "Solo": ("#F1EFE8", "#444441"),
    "Couple": ("#FBEAF0", "#72243E"),
    "Group": ("#EAF3DE", "#3B6D11"),
}
CARD_EMOJIS = ["🏔", "🌵", "🌆", "🏖", "🌲"]
BG_COLORS = ["#E1F5EE", "#FAEEDA", "#EEEDFE", "#FAECE7", "#E6F1FB"]

if "compare_bucket" not in st.session_state:
    st.session_state.compare_bucket = []

cols = st.columns(len(cards))
for i, (card, col) in enumerate(zip(cards, cols)):
    with col:
        is_best = card.get("is_best_match", False)
        border = "2px solid #185FA5" if is_best else "1px solid #E8E8E4"

        st.markdown(f"""
        <div style="background:{BG_COLORS[i % len(BG_COLORS)]};
            border-radius:12px 12px 0 0; padding:16px;
            text-align:center; font-size:28px;
            border:{border}; border-bottom:none;">
            {CARD_EMOJIS[i % len(CARD_EMOJIS)]}
        </div>
        """, unsafe_allow_html=True)

        if is_best:
            st.markdown("""<div style="background:#E6F1FB; color:#0C447C;
                font-size:11px; font-weight:500; padding:3px 10px;
                text-align:center; border-left:2px solid #185FA5;
                border-right:2px solid #185FA5;">
                ⭐ Best match</div>""", unsafe_allow_html=True)

        st.markdown(f"**{card['name']}**, {card['state']}")
        st.caption(card.get("match_label", ""))
        st.markdown(f"*{card['why']}*")
        st.markdown(f"🌤 {card.get('weather_summary', '')}")

        fl = card.get("flight_low", 0)
        fh = card.get("flight_high", 0)
        tl = card.get("total_low", 0)
        th = card.get("total_high", 0)
        st.markdown(f"""
        <div style="background:#F5F5F0; border-radius:8px;
            padding:8px 10px; margin:8px 0; font-size:12px;">
            ✈️ Flight: <b>${fl}–${fh}</b><br>
            💰 Total est: <b>${tl}–${th}</b><br>
            <span style="color:#888; font-size:11px;">
                {card.get('booking_tip','')}
            </span>
        </div>
        """, unsafe_allow_html=True)

        badges_html = ""
        for interest in card.get("matched_interests", []):
            bg, fg = INTEREST_COLORS.get(interest, ("#F1EFE8", "#444441"))
            badges_html += (
                f'<span style="background:{bg}; color:{fg}; '
                f'font-size:10px; padding:2px 8px; border-radius:10px; '
                f'margin:2px; display:inline-block;">{interest}</span>'
            )
        st.markdown(badges_html, unsafe_allow_html=True)

        st.markdown("**Top things to do:**")
        for thing in card.get("top_3", [])[:5]:
            st.markdown(f"• {thing}")

        st.markdown("")

        # Add to compare
        in_bucket = any(b["name"] == card["name"] for b in st.session_state.compare_bucket)
        bucket_full = len(st.session_state.compare_bucket) >= 4

        if in_bucket:
            if st.button("✓ In compare", key=f"compare_{i}", use_container_width=True):
                st.session_state.compare_bucket = [
                    b for b in st.session_state.compare_bucket
                    if b["name"] != card["name"]
                ]
                st.rerun()
        elif bucket_full:
            st.button("Compare full (max 4)", key=f"compare_{i}",
                      disabled=True, use_container_width=True)
        else:
            if st.button("+ Add to compare", key=f"compare_{i}", use_container_width=True):
                st.session_state.compare_bucket.append({
                    **card,
                    "search_name": st.session_state.get("trip_name_input", "Search"),
                    "search_params": search_params
                })
                st.rerun()

        if st.button("Plan this trip →", key=f"plan_{i}",
                     use_container_width=True, type="primary"):
            st.session_state["selected_destination"] = card
            st.info("Phase 2 coming soon!")

# ── Compare bar ───────────────────────────────────────────────────────────────
bucket = st.session_state.get("compare_bucket", [])
if bucket:
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        names = " · ".join(b["name"] for b in bucket)
        st.markdown(f"**Compare bucket:** {names} ({len(bucket)}/4)")
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.compare_bucket = []
            st.rerun()
    with col3:
        if st.button("Compare now →", type="primary", use_container_width=True):
            st.switch_page("pages/3_Compare.py")