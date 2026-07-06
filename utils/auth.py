from __future__ import annotations
import streamlit as st
from utils.supabase_client import get_supabase


def get_current_user() -> dict | None:
    """Return current logged-in user from session, or None."""
    return st.session_state.get("user", None)


def is_logged_in() -> bool:
    return get_current_user() is not None


def login_with_google():
    """Trigger Google OAuth via Supabase — redirects to Google."""
    try:
        sb = get_supabase()
        app_url = st.secrets.get("app_url", "http://localhost:8501")
        response = sb.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": app_url,
                "query_params": {"access_type": "offline", "prompt": "consent"}
            }
        })
        if response and response.url:
            # Redirect browser to Google login
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={response.url}">',
                unsafe_allow_html=True
            )
            st.stop()
    except Exception as e:
        st.error(f"Login error: {e}")


def handle_oauth_callback() -> bool:
    """
    Handle OAuth redirect back from Google.
    Supabase appends access_token + refresh_token as URL fragments (#).
    Streamlit can't read fragments, so we use a small JS bridge
    that reads the hash and posts it back as a query param.
    """
    params = st.query_params

    # JS bridge — runs on page load, reads # fragment and reloads with ?token=
    if "access_token" not in params:
        st.markdown("""
        <script>
        (function() {
            const hash = window.location.hash;
            if (hash && hash.includes('access_token')) {
                const params = new URLSearchParams(hash.substring(1));
                const token = params.get('access_token');
                const refresh = params.get('refresh_token');
                if (token) {
                    const url = new URL(window.location.href);
                    url.hash = '';
                    url.searchParams.set('access_token', token);
                    url.searchParams.set('refresh_token', refresh || '');
                    window.location.replace(url.toString());
                }
            }
        })();
        </script>
        """, unsafe_allow_html=True)
        return False

    # We have the token — set session via Supabase
    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token", "")

    if access_token and "user" not in st.session_state:
        try:
            sb = get_supabase()
            session = sb.auth.set_session(access_token, refresh_token)
            if session and session.user:
                st.session_state["user"] = {
                    "id": session.user.id,
                    "email": session.user.email,
                    "name": session.user.user_metadata.get("full_name", "Traveller"),
                    "avatar": session.user.user_metadata.get("avatar_url", "")
                }
                # Clean tokens from URL
                st.query_params.clear()
                st.rerun()
                return True
        except Exception as e:
            st.error(f"Could not complete login: {e}")
            st.query_params.clear()

    return False


def logout():
    """Sign out and clear session."""
    try:
        sb = get_supabase()
        sb.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("user", None)
    st.session_state.pop("compare_bucket", None)
    st.rerun()


def require_login(message: str = "Sign in to save and share your trips.") -> bool:
    """Show login prompt if not logged in. Returns True if logged in."""
    if not is_logged_in():
        st.info(f"🔐 {message}")
        if st.button("Sign in with Google", type="primary", key="login_btn"):
            login_with_google()
        return False
    return True


def render_nav_auth():
    """Render auth section in nav — sign in button or user name + sign out."""
    user = get_current_user()
    if user:
        col1, col2 = st.columns([3, 1])
        with col1:
            name = user.get("name", "").split()[0] if user.get("name") else "Traveller"
            st.markdown(f"👤 **{name}**")
        with col2:
            if st.button("Sign out", key="nav_signout"):
                logout()
    else:
        if st.button("Sign in with Google", type="primary", key="nav_signin"):
            login_with_google()