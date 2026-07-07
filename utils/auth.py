from __future__ import annotations
import streamlit as st
from utils.supabase_client import get_supabase


def get_current_user():
    return st.session_state.get("user", None)


def is_logged_in() -> bool:
    return get_current_user() is not None


def handle_oauth_callback():
    pass


def render_auth_page():
    """Full login/signup page with email and password."""
    st.markdown("## Welcome to TripCraft ✈️")
    st.markdown("Sign in or create an account to save and share trips.")
    st.markdown("")

    tab1, tab2 = st.tabs(["Sign in", "Create account"])

    with tab1:
        email = st.text_input("Email", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_password")
        if st.button("Sign in", type="primary", use_container_width=True, key="signin_btn"):
            if not email or not password:
                st.warning("Please enter email and password.")
            else:
                try:
                    sb = get_supabase()
                    res = sb.auth.sign_in_with_password({"email": email, "password": password})
                    if res.user:
                        st.session_state["user"] = {
                            "id": res.user.id,
                            "email": res.user.email,
                            "name": res.user.user_metadata.get("name", email.split("@")[0]),
                            "avatar": ""
                        }
                        st.success("Signed in!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Sign in failed: {e}")

    with tab2:
        name = st.text_input("Your name", key="signup_name")
        email2 = st.text_input("Email", key="signup_email")
        password2 = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create account", type="primary", use_container_width=True, key="signup_btn"):
            if not name or not email2 or not password2:
                st.warning("Please fill in all fields.")
            elif len(password2) < 6:
                st.warning("Password must be at least 6 characters.")
            else:
                try:
                    sb = get_supabase()
                    res = sb.auth.sign_up({
                        "email": email2,
                        "password": password2,
                        "options": {"data": {"name": name}}
                    })
                    if res.user:
                        st.success("Account created! Please check your email to confirm, then sign in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")


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
        render_auth_page()
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
        if st.button("Sign in", type="primary", key="nav_signin"):
            st.switch_page("pages/5_Login.py")