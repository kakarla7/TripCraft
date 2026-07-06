import streamlit as st

st.set_page_config(
    page_title="TripCraft",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global styles
st.markdown("""
<style>
    /* Hide default Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Clean font and spacing */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Sidebar nav styling */
    .st-sidebar .st-emotion-cache-1cypcdb {
        background: #FAFAF8;
    }

    /* Card style utility */
    .tripcraft-card {
        background: white;
        border: 1px solid #E8E8E4;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #D85A30;
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 500;
    }
    .stButton > button[kind="primary"]:hover {
        background: #C04828;
    }

    /* Tag pill */
    .tag-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        margin: 3px;
        cursor: pointer;
        border: 1px solid #E0DED8;
        background: #F5F5F0;
        color: #555;
    }
    .tag-pill.selected {
        background: #E6F1FB;
        border-color: #185FA5;
        color: #0C447C;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Landing page — redirect to search
st.switch_page("pages/1_Search.py")
