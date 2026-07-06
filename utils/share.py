import uuid
import streamlit as st


def generate_slug() -> str:
    """Generate a short unique share slug e.g. x7k2p9."""
    return uuid.uuid4().hex[:8]


def get_share_url(slug: str, path: str = "results") -> str:
    """Build the full shareable URL for a given slug."""
    app_url = st.secrets.get("app_url", "http://localhost:8501")
    return f"{app_url}/{path}?s={slug}"


def render_share_sheet(share_url: str, title: str = "Check out this trip on TripCraft!"):
    """
    Render the share sheet with three options:
    - Copy link
    - iMessage / SMS (Web Share API)
    - AirDrop / Nearby Share (Web Share API — OS handles it)
    """
    st.markdown("#### Share this trip")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Copy to clipboard via JS
        st.markdown(f"""
        <button onclick="navigator.clipboard.writeText('{share_url}').then(() => {{
            this.textContent = '✓ Copied!';
            setTimeout(() => this.textContent = '📋 Copy link', 2000);
        }})" style="
            width:100%; padding:9px; border-radius:8px;
            border:1px solid #E0DED8; background:#F5F5F0;
            cursor:pointer; font-size:14px; font-weight:500;
        ">📋 Copy link</button>
        <div style="font-size:11px; color:#888; margin-top:4px; word-break:break-all;">
            {share_url}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Web Share API — triggers iMessage, WhatsApp etc on mobile
        st.markdown(f"""
        <button onclick="
            if (navigator.share) {{
                navigator.share({{
                    title: '{title}',
                    url: '{share_url}'
                }});
            }} else {{
                navigator.clipboard.writeText('{share_url}');
                this.textContent = '✓ Link copied!';
            }}
        " style="
            width:100%; padding:9px; border-radius:8px;
            border:1px solid #E0DED8; background:#F5F5F0;
            cursor:pointer; font-size:14px; font-weight:500;
        ">💬 Send via message</button>
        <div style="font-size:11px; color:#888; margin-top:4px;">
            iMessage · WhatsApp · SMS
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # AirDrop / Nearby Share — same Web Share API, OS picks the method
        st.markdown(f"""
        <button onclick="
            if (navigator.share) {{
                navigator.share({{
                    title: '{title}',
                    url: '{share_url}'
                }});
            }} else {{
                alert('AirDrop / Nearby Share is available on mobile devices.');
            }}
        " style="
            width:100%; padding:9px; border-radius:8px;
            border:1px solid #E0DED8; background:#F5F5F0;
            cursor:pointer; font-size:14px; font-weight:500;
        ">📡 AirDrop / Nearby</button>
        <div style="font-size:11px; color:#888; margin-top:4px;">
            iOS AirDrop · Android Nearby
        </div>
        """, unsafe_allow_html=True)
