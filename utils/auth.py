from __future__ import annotations
import streamlit as st

# Auth stub — Google OAuth stubbed out until Supabase package issue is resolved
# Login button will show a demo user so you can test the full app flow

def get_current_user():
    return st.session_state.get("user", None)

def is_logged_in() -> bool:
    return get_current_user() is not None

def login_with_google():
    # Stub — sets a demo user directly so you can test save/share flow
    st.session_state["user"] = {
        "id": "demo-user-001",
        "email": "demo@tripcraft.app",
        "name": "Demo User",
        "avatar": ""
    }
    st.rerun()

def handle_oauth_callback():
    # No-op stub
    return False

def logout():
    st.session_state.pop("user", None)
    st.rerun()

def require_login(message: str = "Sign in to save and share your trips."):
    if not is_logged_in():
        st.info(f"🔐 {message}")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Sign in with Google", type="primary"):
                login_with_google()
        return False
    return True