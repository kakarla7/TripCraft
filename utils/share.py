from __future__ import annotations
import uuid
import streamlit as st


def generate_slug() -> str:
    """Generate a short unique share slug e.g. x7k2p9ab."""
    return uuid.uuid4().hex[:8]


def get_share_url(slug: str, page: str = "Results") -> str:
    """Build the full shareable URL."""
    app_url = st.secrets.get("app_url", "http://localhost:8501")
    # Remove trailing slash
    app_url = app_url.rstrip("/")
    return f"{app_url}/{page}?s={slug}"


def render_share_sheet(share_url: str, title: str = "Check out this trip on TripCraft!"):
    """
    Render share options:
    - Copy link
    - iMessage / SMS via Web Share API
    - AirDrop / Nearby Share via Web Share API
    """
    st.markdown("**Share this search:**")
    st.code(share_url, language=None)

    col1, col2, col3 = st.columns(3)

    with col1:
        # Copy to clipboard
        st.markdown(f"""
        <button onclick="navigator.clipboard.writeText('{share_url}').then(() => {{
            this.textContent = '✓ Copied!';
            setTimeout(() => this.textContent = '📋 Copy link', 2000);
        }})" style="width:100%;padding:8px;border-radius:8px;
            border:1px solid #E0DED8;background:#F5F5F0;
            cursor:pointer;font-size:13px;font-weight:500;">
            📋 Copy link
        </button>
        """, unsafe_allow_html=True)

    with col2:
        # Web Share API — iMessage, WhatsApp, SMS on mobile
        st.markdown(f"""
        <button onclick="
            if(navigator.share){{
                navigator.share({{title:'{title}',url:'{share_url}'}});
            }} else {{
                navigator.clipboard.writeText('{share_url}');
                this.textContent='✓ Link copied!';
            }}
        " style="width:100%;padding:8px;border-radius:8px;
            border:1px solid #E0DED8;background:#F5F5F0;
            cursor:pointer;font-size:13px;font-weight:500;">
            💬 Send via message
        </button>
        <div style="font-size:11px;color:#888;margin-top:3px;">
            iMessage · WhatsApp · SMS
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Same Web Share API — OS shows AirDrop on iOS, Nearby Share on Android
        st.markdown(f"""
        <button onclick="
            if(navigator.share){{
                navigator.share({{title:'{title}',url:'{share_url}'}});
            }} else {{
                alert('AirDrop and Nearby Share are available on mobile.');
            }}
        " style="width:100%;padding:8px;border-radius:8px;
            border:1px solid #E0DED8;background:#F5F5F0;
            cursor:pointer;font-size:13px;font-weight:500;">
            📡 AirDrop / Nearby
        </button>
        <div style="font-size:11px;color:#888;margin-top:3px;">
            iOS AirDrop · Android Nearby
        </div>
        """, unsafe_allow_html=True)