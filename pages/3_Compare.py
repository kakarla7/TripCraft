from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="TripCraft — Compare", page_icon="✈️", layout="wide")

from utils.auth import render_nav_auth
from utils.supabase_client import get_user_searches
from utils.auth import get_current_user, is_logged_in

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
    st.button(label, use_container_width=True, disabled=True)
with col_auth:
    render_nav_auth()

st.divider()
st.markdown("## ⚖️ Compare destinations")

# ── Get destinations to compare ───────────────────────────────────────────────
bucket = st.session_state.get("compare_bucket", [])

# Also allow picking from saved searches if logged in
if is_logged_in():
    user = get_current_user()
    try:
        saved_searches = get_user_searches(user["id"])
    except Exception:
        saved_searches = []

    if saved_searches:
        st.markdown("**Add more destinations from your saved searches:**")
        for search in saved_searches:
            name = search.get("name", "Unnamed search")
            results = search.get("results", [])
            params = search.get("search_params", {})
            with st.expander(f"📍 {name} · {params.get('origin','?')} · {params.get('month','?')}"):
                dest_cols = st.columns(len(results)) if results else []
                for j, (dest, dc) in enumerate(zip(results, dest_cols)):
                    with dc:
                        in_bucket = any(b["name"] == dest["name"]
                                        for b in st.session_state.compare_bucket)
                        bucket_full = len(st.session_state.compare_bucket) >= 4
                        st.markdown(f"**{dest['name']}**, {dest['state']}")
                        st.caption(dest.get("match_label", ""))
                        if in_bucket:
                            if st.button("✓ In compare", key=f"saved_{search['id']}_{j}",
                                         use_container_width=True):
                                st.session_state.compare_bucket = [
                                    b for b in st.session_state.compare_bucket
                                    if b["name"] != dest["name"]
                                ]
                                st.rerun()
                        elif bucket_full:
                            st.button("Full (max 4)", key=f"saved_{search['id']}_{j}",
                                      disabled=True, use_container_width=True)
                        else:
                            if st.button("+ Add", key=f"saved_{search['id']}_{j}",
                                         use_container_width=True):
                                st.session_state.compare_bucket.append({
                                    **dest,
                                    "search_name": name,
                                    "search_params": params
                                })
                                st.rerun()

# Update bucket after picker
bucket = st.session_state.get("compare_bucket", [])

if len(bucket) < 2:
    st.info("Add at least 2 destinations to compare. Use '+ Add to compare' on the results page or pick from your saved searches above.")
    if st.button("← Go to search", type="primary"):
        st.switch_page("pages/1_Search.py")
    st.stop()

st.markdown("---")

# ── Compare bucket header ─────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"**Comparing {len(bucket)} destinations**")
with col2:
    if st.button("Clear all", use_container_width=True):
        st.session_state.compare_bucket = []
        st.rerun()

st.markdown("")

# ── Amazon-style compare table ────────────────────────────────────────────────
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

def win_style(val, all_vals, higher_is_better=True):
    """Return green style if this value wins."""
    try:
        nums = [float(v) for v in all_vals if v is not None]
        if not nums:
            return ""
        best = max(nums) if higher_is_better else min(nums)
        if float(val) == best:
            return "color:#3B6D11; font-weight:600;"
    except Exception:
        pass
    return ""

# Header row
header_cols = st.columns([2] + [1] * len(bucket))
with header_cols[0]:
    st.markdown("**Destination**")
for i, dest in enumerate(bucket):
    with header_cols[i + 1]:
        is_best = dest.get("is_best_match", False)
        st.markdown(
            f"**{dest['name']}**{'  ⭐' if is_best else ''}\n\n"
            f"*{dest['state']}*\n\n"
            f"<small style='color:#888'>{dest.get('search_name','')}</small>",
            unsafe_allow_html=True
        )
        if st.button("✕ Remove", key=f"remove_{i}", use_container_width=True):
            st.session_state.compare_bucket.pop(i)
            st.rerun()

st.markdown("---")

# Match score row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Match score**")
scores = [dest.get("match_score", 0) for dest in bucket]
for i, dest in enumerate(bucket):
    with row[i + 1]:
        score = dest.get("match_score", 0)
        style = win_style(score, scores, higher_is_better=True)
        st.markdown(f"<span style='{style}'>{dest.get('match_label', f'{score}/5')}</span>",
                    unsafe_allow_html=True)

# Interests matched row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Interests matched**")
all_interests = set()
for dest in bucket:
    all_interests.update(dest.get("matched_interests", []))

for i, dest in enumerate(bucket):
    with row[i + 1]:
        matched = dest.get("matched_interests", [])
        badges = ""
        for interest in all_interests:
            if interest in matched:
                bg, fg = INTEREST_COLORS.get(interest, ("#E1F5EE", "#0F6E56"))
                badges += (f'<span style="background:{bg};color:{fg};'
                           f'font-size:10px;padding:2px 7px;border-radius:8px;'
                           f'margin:2px;display:inline-block;">{interest}</span>')
            else:
                badges += (f'<span style="background:#F1EFE8;color:#aaa;'
                           f'font-size:10px;padding:2px 7px;border-radius:8px;'
                           f'margin:2px;display:inline-block;text-decoration:line-through;">'
                           f'{interest}</span>')
        st.markdown(badges, unsafe_allow_html=True)

st.markdown("---")

# Weather row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Weather**")
for i, dest in enumerate(bucket):
    with row[i + 1]:
        st.markdown(f"🌤 {dest.get('weather_summary', '—')}")

# Flight cost row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Flight cost**")
flight_lows = [dest.get("flight_low", 9999) for dest in bucket]
for i, dest in enumerate(bucket):
    with row[i + 1]:
        fl = dest.get("flight_low", 0)
        fh = dest.get("flight_high", 0)
        style = win_style(fl, flight_lows, higher_is_better=False)
        st.markdown(f"<span style='{style}'>✈️ ${fl}–${fh}</span>",
                    unsafe_allow_html=True)

# Total cost row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Total estimated cost**")
total_lows = [dest.get("total_low", 9999) for dest in bucket]
for i, dest in enumerate(bucket):
    with row[i + 1]:
        tl = dest.get("total_low", 0)
        th = dest.get("total_high", 0)
        style = win_style(tl, total_lows, higher_is_better=False)
        st.markdown(f"<span style='{style}'>💰 ${tl}–${th}</span>",
                    unsafe_allow_html=True)

# Cost tier row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Cost tier**")
for i, dest in enumerate(bucket):
    with row[i + 1]:
        tier = dest.get("cost_tier", "$$")
        color = "#3B6D11" if tier == "$" else "#854F0B" if tier == "$$$" else "#185FA5"
        st.markdown(f"<span style='color:{color};font-weight:600'>{tier}</span>",
                    unsafe_allow_html=True)

st.markdown("---")

# Kid friendly row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Kid friendly**")
for i, dest in enumerate(bucket):
    with row[i + 1]:
        matched = dest.get("matched_interests", [])
        if "Kid friendly" in matched:
            st.markdown("✅ Yes")
        else:
            st.markdown("❌ No")

# Senior friendly row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Senior friendly**")
for i, dest in enumerate(bucket):
    with row[i + 1]:
        matched = dest.get("matched_interests", [])
        if "Senior friendly" in matched:
            st.markdown("✅ Yes")
        else:
            st.markdown("❌ No")

# Drive time row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Drive time**")
drive_times = [dest.get("drive_hours", 9999) for dest in bucket]
for i, dest in enumerate(bucket):
    with row[i + 1]:
        hrs = dest.get("drive_hours", 0)
        style = win_style(hrs, drive_times, higher_is_better=False)
        st.markdown(f"<span style='{style}'>🚗 {hrs}h</span>",
                    unsafe_allow_html=True)

st.markdown("---")

# Top 5 things to do row
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Top things to do**")
for i, dest in enumerate(bucket):
    with row[i + 1]:
        for thing in dest.get("top_3", [])[:5]:
            st.markdown(f"• {thing}")

st.markdown("---")

# Search context footer
row = st.columns([2] + [1] * len(bucket))
with row[0]:
    st.markdown("**Search context**")
for i, dest in enumerate(bucket):
    with row[i + 1]:
        sp = dest.get("search_params", {})
        booking = {
            "3_months": "Book 3+ months out",
            "4_8_weeks": "Book 4–8 weeks out",
            "last_minute": "Last minute"
        }.get(sp.get("booking_window", ""), "")
        st.markdown(
            f"<small style='color:#888'>"
            f"{sp.get('origin','?')} · {sp.get('month','?')} · "
            f"{sp.get('days','?')} days<br>{booking}</small>",
            unsafe_allow_html=True
        )

st.markdown("")

# Plan buttons
plan_cols = st.columns([2] + [1] * len(bucket))
with plan_cols[0]:
    st.markdown("**Ready to plan?**")
for i, dest in enumerate(bucket):
    with plan_cols[i + 1]:
        if st.button(f"Plan {dest['name']} →", key=f"plan_{i}",
                     type="primary", use_container_width=True):
            st.session_state["selected_destination"] = dest
            st.info("Phase 2 coming soon!")