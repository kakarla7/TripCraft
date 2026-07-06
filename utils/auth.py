from __future__ import annotations
import streamlit as st
from utils.supabase_client import get_supabase


def get_current_user() -> dict | None:
    return st.session_state.get("user", None)


def is_logged_in() -> bool:
    return get_current_user() is not None


def login_with_google():
    """Trigger Google OAuth via Supabase."""
    try:
        sb = get_supabase()
        app_url = st.secrets.get("app_url", "http://localhost:8501")
        response = sb.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": app_url,
            }
        })
        if response and response.url:
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={response.url}">',
                unsafe_allow_html=True
            )
            st.stop()
    except Exception as e:
        st.error(f"Login error: {e}")


def handle_oauth_callback():
    """
    Handle OAuth callback — Supabase returns tokens as URL query params.
    We extract them and create a session.
    """
    params = st.query_params

    # Already logged in
    if "user" in st.session_state:
        return True

    # Check for error from OAuth provider
    if "error" in params:
        st.error(f"Login failed: {params.get('error_description', params.get('error'))}")
        st.query_params.clear()
        return False

    # Supabase returns access_token as query param after redirect
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
    for key in ["user", "compare_bucket", "results", "search_params", "current_share_slug"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_login(message: str = "Sign in to save and share your trips.") -> bool:
    if not is_logged_in():
        st.info(f"🔐 {message}")
        if st.button("Sign in with Google", type="primary", key="login_btn"):
            login_with_google()
        return False
    return True


def render_nav_auth():
    """Render auth section in nav."""
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