from __future__ import annotations
import streamlit as st


def render_tag_selector(
    options: list,
    selected: list,
    key_prefix: str,
    color_selected: str = "#E6F1FB",
    border_selected: str = "#185FA5",
    text_selected: str = "#0C447C"
) -> list:
    """
    Renders a mobile-friendly wrapped tag selector.
    Returns the updated list of selected items.
    """
    # Build HTML tags with click handling via form buttons
    cols = st.columns(min(len(options), 5))
    result = list(selected)

    for i, option in enumerate(options):
        with cols[i % 5]:
            is_on = option in result
            bg = color_selected if is_on else "#F5F5F0"
            border = border_selected if is_on else "#E0DED8"
            color = text_selected if is_on else "#555"
            weight = "600" if is_on else "400"
            prefix = "✓ " if is_on else ""

            if st.button(
                f"{prefix}{option}",
                key=f"{key_prefix}_{i}",
                use_container_width=True,
            ):
                if option in result:
                    result.remove(option)
                else:
                    result.append(option)
                return result

    return result


MOBILE_CSS = """
<style>
/* Mobile responsive overrides */
@media (max-width: 768px) {
    /* Stack columns on mobile */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }

    /* Make cards full width on mobile */
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        min-width: 100% !important;
        width: 100% !important;
    }

    /* Reduce padding on mobile */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Make nav wrap on mobile */
    .stButton button {
        font-size: 12px !important;
        padding: 4px 8px !important;
    }

    /* Full width inputs on mobile */
    .stSelectbox, .stNumberInput, .stTextInput {
        width: 100% !important;
    }
}

/* Compare table mobile */
.compare-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
</style>
"""


def inject_mobile_css():
    """Inject mobile responsive CSS into every page."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)