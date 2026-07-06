import streamlit as st
from utils.auth import get_current_user, is_logged_in, require_login
from utils.share import generate_slug, get_share_url, render_share_sheet
from utils.supabase_client import save_search, get_search_by_slug

st.set_page_config(page_title="TripCraft — Results", page_icon="✈️", layout="wide")

# ── Load results — from session OR from share slug ─────────────────────────
cards = None
search_params = None
share_slug = st.query_params.get("s", None)

if share_slug:
    # Someone opened a share link
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
col_back, col_title = st.columns([1, 5])
with col_back:
    if st.button("← New search"):
        st.switch_page("pages/1_Search.py")
with col_title:
    p = search_params or {}
    st.markdown(f"### {len(cards)} destinations matched for {p.get('month','your trip')} · "
                f"{p.get('days','?')} days · from {p.get('origin','your city')}")

st.divider()

# ── Save + Share ───────────────────────────────────────────────────────────────
col_save, col_compare = st.columns([2, 1])

with col_save:
    if "current_share_slug" not in st.session_state:
        if st.button("💾 Save & Share these results", type="primary"):
            if require_login("Sign in to save and share your results."):
                user = get_current_user()
                slug = generate_slug()
                try:
                    save_search(user["id"], search_params, cards, slug)
                    st.session_state["current_share_slug"] = slug
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save: {e}")
    else:
        slug = st.session_state["current_share_slug"]
        share_url = get_share_url(slug, "results")
        render_share_sheet(share_url)

with col_compare:
    if st.button("⚖️ Compare two trips"):
        st.switch_page("pages/3_Compare.py")

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

cols = st.columns(len(cards))
for i, (card, col) in enumerate(zip(cards, cols)):
    with col:
        is_best = card.get("is_best_match", False)
        border = "2px solid #185FA5" if is_best else "1px solid #E8E8E4"
        bg_colors = ["#E1F5EE", "#FAEEDA", "#EEEDFE", "#FAECE7", "#E6F1FB"]

        with st.container():
            # Card header
            st.markdown(f"""
            <div style="background:{bg_colors[i % len(bg_colors)]};
                border-radius:12px 12px 0 0; padding:16px;
                text-align:center; font-size:28px; border:{border};
                border-bottom:none;">
                {CARD_EMOJIS[i % len(CARD_EMOJIS)]}
            </div>
            """, unsafe_allow_html=True)

            if is_best:
                st.markdown("""<div style="background:#E6F1FB; color:#0C447C;
                    font-size:11px; font-weight:500; padding:3px 10px;
                    text-align:center; border-left:2px solid #185FA5;
                    border-right:2px solid #185FA5;">
                    ⭐ Best match</div>""", unsafe_allow_html=True)

            # Card body
            st.markdown(f"**{card['name']}**, {card['state']}")
            st.caption(card.get("match_label", ""))
            st.markdown(f"*{card['why']}*")
            st.markdown("")

            # Weather
            st.markdown(f"🌤 {card.get('weather_summary', 'Weather info unavailable')}")

            # Price block
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

            # Interest badges
            badges_html = ""
            for interest in card.get("matched_interests", []):
                bg, fg = INTEREST_COLORS.get(interest, ("#F1EFE8", "#444441"))
                badges_html += (f'<span style="background:{bg}; color:{fg}; '
                                f'font-size:10px; padding:2px 8px; border-radius:10px; '
                                f'margin:2px; display:inline-block;">{interest}</span>')
            st.markdown(badges_html, unsafe_allow_html=True)

            # Top 3 things
            st.markdown("**Top things to do:**")
            for thing in card.get("top_3", []):
                st.markdown(f"• {thing}")

            st.markdown("")
            if st.button(f"Plan this trip →", key=f"plan_{i}", use_container_width=True, type="primary"):
                st.session_state["selected_destination"] = card
                # Phase 2 — coming soon
                st.info("Phase 2 coming soon! Full itinerary planner.")
