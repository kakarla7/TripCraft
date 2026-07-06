from __future__ import annotations
import streamlit as st
from streamlit_google_auth import Authenticate


def get_authenticator() -> Authenticate:
    """Get or create the Google authenticator."""
    if "authenticator" not in st.session_state:
        app_url = st.secrets.get("app_url", "http://localhost:8501")
        st.session_state["authenticator"] = Authenticate(
            secret_credentials_path="google_credentials.json",
            redirect_uri=app_url,
            cookie_name="tripcraft_auth",
            cookie_key=st.secrets.get("cookie_key", "tripcraft_secret_key_2024"),
            cookie_expiry_days=30
        )
    return st.session_state["authenticator"]


def handle_oauth_callback() -> bool:
    """Check authentication status on every page load."""
    authenticator = get_authenticator()
    authenticator.check_authentification()

    if st.session_state.get("connected"):
        if "user" not in st.session_state:
            user_info = st.session_state.get("user_info", {})
            st.session_state["user"] = {
                "id": user_info.get("sub", user_info.get("email", "unknown")),
                "email": user_info.get("email", ""),
                "name": user_info.get("name", "Traveller"),
                "avatar": user_info.get("picture", "")
            }
        return True
    return False


def get_current_user():
    return st.session_state.get("user", None)


def is_logged_in() -> bool:
    return st.session_state.get("connected", False)


def render_login_button():
    """Render the Google sign in button."""
    authenticator = get_authenticator()
    authenticator.login()


def logout():
    authenticator = get_authenticator()
    authenticator.logout()
    for key in ["user", "compare_bucket", "results", "search_params",
                "current_share_slug", "connected", "user_info"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_login(message: str = "Sign in to save and share your trips.") -> bool:
    if not is_logged_in():
        st.info(f"🔐 {message}")
        render_login_button()
        return False
    return True


def render_nav_auth():
    user = get_current_user()
    if is_logged_in() and user:
        col1, col2 = st.columns([3, 1])
        with col1:
            name = user.get("name", "").split()[0] if user.get("name") else "Traveller"
            st.markdown(f"👤 **{name}**")
        with col2:
            if st.button("Sign out", key="nav_signout"):
                logout()
    else:
        render_login_button()