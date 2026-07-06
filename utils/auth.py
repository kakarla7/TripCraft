from __future__ import annotations
import streamlit as st

from utils.supabase_client import get_supabase


def get_current_user():
    return st.session_state.get("user", None)


def is_logged_in() -> bool:
    return get_current_user() is not None


def get_google_auth_url() -> str | None:
    """Get Google OAuth URL from Supabase."""
    try:
        sb = get_supabase()
        app_url = st.secrets.get("app_url", "http://localhost:8501")
        response = sb.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": app_url}
        })
        return response.url if response and response.url else None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None


def handle_oauth_callback() -> bool:
    """
    Supabase returns tokens in URL hash (#access_token=...).
    This JS snippet runs on every page load, reads the hash,
    and rewrites the URL as query params (?access_token=...)
    so Streamlit can read them server-side.
    """
    if "user" in st.session_state:
        return True

    # Inject JS that converts hash params to query params
    st.html("""
        <script>
        (function() {
            const hash = window.location.hash;
            if (hash && hash.includes('access_token')) {
                const params = new URLSearchParams(hash.replace('#', ''));
                const access_token = params.get('access_token');
                const refresh_token = params.get('refresh_token') || '';
                if (access_token) {
                    const url = window.location.href.split('#')[0];
                    const newUrl = url + 
                        (url.includes('?') ? '&' : '?') + 
                        'access_token=' + encodeURIComponent(access_token) +
                        '&refresh_token=' + encodeURIComponent(refresh_token);
                    window.location.replace(newUrl);
                }
            }
        })();
        </script>
    """)

    # Now check query params for tokens
    params = st.query_params

    if "error" in params:
        st.error(f"Login failed: {params.get('error_description', params.get('error'))}")
        st.query_params.clear()
        return False

    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token", "")

    if access_token:
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
                st.query_params.clear()
                st.rerun()
                return True
        except Exception as e:
            st.error(f"Could not complete login: {e}")
            st.query_params.clear()

    return False


def logout():
    try:
        sb = get_supabase()
        sb.auth.sign_out()
    except Exception:
        pass
    for key in ["user", "compare_bucket", "results", "search_params", "current_share_slug"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_login(message: str = "Sign in to save and share your trips.") -> bool:
    if not is_logged_in():
        st.info(f"🔐 {message}")
        auth_url = get_google_auth_url()
        if auth_url:
            st.link_button("Sign in with Google", auth_url, type="primary")
        return False
    return True


def render_nav_auth():
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
        auth_url = get_google_auth_url()
        if auth_url:
            st.link_button("Sign in with Google", auth_url, type="primary")