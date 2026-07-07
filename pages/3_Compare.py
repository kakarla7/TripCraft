from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="TripCraft — Compare", page_icon="✈️", layout="wide")

from utils.auth import render_nav_auth, get_current_user, is_logged_in
from utils.supabase_client import get_user_searches, get_comparison_by_slug

# ── Load shared comparison if opened via link ─────────────────────────────────
share_slug = st.query_params.get("s", None)
if share_slug:
    try:
        saved = get_comparison_by_slug(share_slug)
        if saved:
            st.session_state["compare_bucket"] = saved["destinations"]
            st.info("👀 You're viewing a shared TripCraft comparison.")
    except Exception:
        st.error("This share link has expired or doesn't exist.")

# ── Nav ───────────────────────────────────────────────────────────────────────
col_logo, col_search, col_trips, col_compare, col_auth = st.columns([2, 1, 1, 1, 2])
with col_logo:
    if st.button("✈️ TripCraft", key="logo"):
        st.switch_page("app.py")
with col_search:
    if st.button("Search", use_container_width=True):
        st.switch_page("pages/1_Search.py")
with col_trips:
    if st.button("My Trips", use_container_width=True):
        st.switch_page("pages/4_My_Trips.py")
with col_compare:
    bucket = st.session_state.get("compare_bucket", [])
    label = f"Compare ({len(bucket)})" if bucket else "Compare"
    st.button(label, use_container_width=True, disabled=True)
with col_auth:
    render_nav_auth()

st.divider()
st.markdown("## ⚖️ Compare destinations")

# ── Initialise bucket ─────────────────────────────────────────────────────────
if "compare_bucket" not in st.session_state:
    st.session_state.compare_bucket = []

# ── Pick from saved searches ──────────────────────────────────────────────────
if is_logged_in():
    user = get_current_user()
    try:
        saved_searches = get_user_searches(user["id"])
    except Exception:
        saved_searches = []

    if saved_searches:
        st.markdown("**Add destinations from your saved searches:**")
        for search in saved_searches:
            sname = search.get("name", "Unnamed search")
            results = search.get("results", [])
            params = search.get("search_params", {})
            with st.expander(
                f"📍 {sname} · {params.get('origin','?')} · {params.get('month','?')}"
            ):
                dest_cols = st.columns(len(results)) if results else []
                for j, (dest, dc) in enumerate(zip(results, dest_cols)):
                    with dc:
                        in_bucket = any(
                            b["name"] == dest["name"]
                            for b in st.session_state.compare_bucket
                        )
                        bucket_full = len(st.session_state.compare_bucket) >= 4
                        st.markdown(f"**{dest['name']}**, {dest['state']}")
                        st.caption(dest.get("match_label", ""))
                        if in_bucket:
                            if st.button("✓ In compare",
                                         key=f"saved_{search['id']}_{j}",
                                         use_container_width=True):
                                st.session_state.compare_bucket = [
                                    b for b in st.session_state.compare_bucket
                                    if b["name"] != dest["name"]
                                ]
                                st.rerun()
                        elif bucket_full:
                            st.button("Full (max 4)",
                                      key=f"saved_{search['id']}_{j}",
                                      disabled=True,
                                      use_container_width=True)
                        else:
                            if st.button("+ Add",
                                         key=f"saved_{search['id']}_{j}",
                                         use_container_width=True):
                                st.session_state.compare_bucket.append({
                                    **dest,
                                    "search_name": sname,
                                    "search_params": params
                                })
                                st.rerun()

bucket = st.session_state.get("compare_bucket", [])

if len(bucket) < 2:
    st.markdown("""
    <div style="text-align:center; padding:2.5rem; background:#F5F5F0;
        border-radius:12px; margin:1rem 0;">
        <div style="font-size:36px; margin-bottom:0.75rem;">⚖️</div>
        <div style="font-weight:500; font-size:15px; color:#1A1A1A;
            margin-bottom:0.5rem;">Add at least 2 destinations to compare</div>
        <div style="font-size:13px; color:#666;">
            Use "+ Add to compare" on the results page, or pick from your
            saved searches above.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Go to search", type="primary"):
        st.switch_page("pages/1_Search.py")
    st.stop()

# ── Clear all button ──────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"**Comparing {len(bucket)} destinations**")
with col2:
    if st.button("Clear all", use_container_width=True):
        st.session_state.compare_bucket = []
        st.rerun()

# ── Build HTML compare table with sticky first column ─────────────────────────
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

def win_color(val, all_vals, higher_is_better=True):
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

# Collect all interests across bucket
all_interests = set()
for dest in bucket:
    all_interests.update(dest.get("matched_interests", []))

# Build rows data
def dest_header(dest):
    best = "⭐ " if dest.get("is_best_match") else ""
    src = dest.get("search_name", "")
    return f"""
        <div style="font-weight:600;font-size:14px">{best}{dest['name']}</div>
        <div style="color:#666;font-size:12px">{dest['state']}</div>
        <div style="color:#aaa;font-size:11px">{src}</div>
    """

def interest_badges(dest):
    matched = dest.get("matched_interests", [])
    badges = ""
    for interest in sorted(all_interests):
        if interest in matched:
            bg, fg = INTEREST_COLORS.get(interest, ("#E1F5EE", "#0F6E56"))
            badges += (f'<span style="background:{bg};color:{fg};font-size:10px;'
                      f'padding:2px 6px;border-radius:8px;margin:2px;'
                      f'display:inline-block;">{interest}</span>')
        else:
            badges += (f'<span style="background:#F1EFE8;color:#ccc;font-size:10px;'
                      f'padding:2px 6px;border-radius:8px;margin:2px;'
                      f'display:inline-block;text-decoration:line-through;">'
                      f'{interest}</span>')
    return badges

scores = [dest.get("match_score", 0) for dest in bucket]
flight_lows = [dest.get("flight_low", 9999) for dest in bucket]
total_lows = [dest.get("total_low", 9999) for dest in bucket]
drive_times = [dest.get("drive_hours", 9999) for dest in bucket]

rows = [
    ("Destination", [dest_header(d) for d in bucket]),
    ("Match score", [
        f"<span style='{win_color(d.get('match_score',0), scores, True)}'>"
        f"{d.get('match_label', f'{d.get(\"match_score\",0)}/5')}</span>"
        for d in bucket
    ]),
    ("Interests", [interest_badges(d) for d in bucket]),
    ("Weather", [f"🌤 {d.get('weather_summary','—')}" for d in bucket]),
    ("Flight cost", [
        f"<span style='{win_color(d.get(\"flight_low\",9999), flight_lows, False)}'>"
        f"✈️ ${d.get('flight_low',0)}–${d.get('flight_high',0)}</span>"
        for d in bucket
    ]),
    ("Total cost", [
        f"<span style='{win_color(d.get(\"total_low\",9999), total_lows, False)}'>"
        f"💰 ${d.get('total_low',0)}–${d.get('total_high',0)}</span>"
        for d in bucket
    ]),
    ("Cost tier", [
        f"<span style='color:{'#3B6D11' if d.get('cost_tier')=='$' else '#854F0B' if d.get('cost_tier')=='$$$' else '#185FA5'};font-weight:600'>"
        f"{d.get('cost_tier','$$')}</span>"
        for d in bucket
    ]),
    ("Kid friendly", [
        "✅ Yes" if "Kid friendly" in d.get("matched_interests",[]) else "❌ No"
        for d in bucket
    ]),
    ("Senior friendly", [
        "✅ Yes" if "Senior friendly" in d.get("matched_interests",[]) else "❌ No"
        for d in bucket
    ]),
    ("Drive time", [
        f"<span style='{win_color(d.get(\"drive_hours\",9999), drive_times, False)}'>"
        f"🚗 {d.get('drive_hours',0)}h</span>"
        for d in bucket
    ]),
    ("Top things to do", [
        "<br>".join(f"• {t}" for t in d.get("top_3",[])[:5])
        for d in bucket
    ]),
    ("Search context", [
        f"<small style='color:#888'>"
        f"{d.get('search_params',{}).get('origin','?')} · "
        f"{d.get('search_params',{}).get('month','?')} · "
        f"{d.get('search_params',{}).get('days','?')} days</small>"
        for d in bucket
    ]),
]

# Build the HTML table
col_width = max(160, int(600 / len(bucket)))
header_cells = "".join(
    f"<th style='min-width:{col_width}px;padding:12px 14px;"
    f"background:#fff;border-bottom:2px solid #E8E8E4;"
    f"vertical-align:top;'>{dest_header(d)}</th>"
    for d in bucket
)

body_rows = ""
for i, (label, cells) in enumerate(rows):
    bg = "#FAFAF8" if i % 2 == 0 else "#fff"
    cell_html = "".join(
        f"<td style='min-width:{col_width}px;padding:10px 14px;"
        f"background:{bg};border-bottom:1px solid #F0F0EC;"
        f"font-size:13px;vertical-align:top;'>{cell}</td>"
        for cell in cells
    )
    body_rows += f"""
    <tr>
        <td style="padding:10px 14px;background:{bg};
            border-bottom:1px solid #F0F0EC;
            font-weight:500;font-size:13px;color:#444;
            position:sticky;left:0;z-index:1;
            min-width:140px;max-width:140px;
            box-shadow:2px 0 4px rgba(0,0,0,0.06);">
            {label}
        </td>
        {cell_html}
    </tr>
    """

table_html = f"""
<div style="overflow-x:auto;border-radius:12px;
    border:1px solid #E8E8E4;margin:1rem 0;">
    <table style="border-collapse:collapse;width:100%;min-width:500px;">
        <thead>
            <tr>
                <th style="min-width:140px;max-width:140px;padding:12px 14px;
                    background:#F5F5F0;border-bottom:2px solid #E8E8E4;
                    position:sticky;left:0;z-index:2;
                    box-shadow:2px 0 4px rgba(0,0,0,0.06);
                    font-size:13px;color:#666;font-weight:500;">
                    Attribute
                </th>
                {header_cells}
            </tr>
        </thead>
        <tbody>
            {body_rows}
        </tbody>
    </table>
</div>
"""

st.markdown(table_html, unsafe_allow_html=True)

# ── Remove individual destinations ────────────────────────────────────────────
st.markdown("**Remove destinations:**")
remove_cols = st.columns(len(bucket))
for i, (dest, col) in enumerate(zip(bucket, remove_cols)):
    with col:
        if st.button(f"✕ Remove {dest['name']}", key=f"remove_{i}",
                     use_container_width=True):
            st.session_state.compare_bucket.pop(i)
            st.rerun()

# ── Plan buttons ──────────────────────────────────────────────────────────────
st.markdown("**Ready to plan?**")
plan_cols = st.columns(len(bucket))
for i, (dest, col) in enumerate(zip(bucket, plan_cols)):
    with col:
        if st.button(f"Plan {dest['name']} →", key=f"plan_{i}",
                     type="primary", use_container_width=True):
            st.session_state["selected_destination"] = dest
            st.info("Phase 2 coming soon!")

# ── Save + Share ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Share this comparison")

if "compare_share_slug" not in st.session_state:
    col_name, col_save = st.columns([3, 1])
    with col_name:
        compare_name = st.text_input(
            "Name this comparison",
            placeholder="e.g. Southwest vs East Coast",
            key="compare_name_input"
        )
    with col_save:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save & Share", type="primary", key="save_compare_btn"):
            if not is_logged_in():
                st.warning("🔐 Sign in to save and share comparisons.")
            else:
                from utils.supabase_client import save_comparison
                from utils.share import generate_slug
                user = get_current_user()
                name = compare_name.strip() or "My comparison"
                slug = generate_slug()
                try:
                    save_comparison(user["id"], name, bucket, slug)
                    st.session_state["compare_share_slug"] = slug
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save: {e}")
else:
    from utils.share import get_share_url, render_share_sheet
    slug = st.session_state["compare_share_slug"]
    share_url = get_share_url(slug, "Compare")
    st.success("✅ Saved!")
    render_share_sheet(share_url, title="Check out this trip comparison on TripCraft!")