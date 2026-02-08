"""UI styling helpers for Streamlit."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


def apply_global_styles(css_path: str | Path | None = None) -> None:
    """Inject global CSS styles into the Streamlit app."""
    if css_path is None:
        css_path = Path(__file__).resolve().parents[1] / "assets" / "styles.css"
    css_file = Path(css_path)

    try:
        css = css_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return

    # CSS file contains raw rules (no <style> wrapper).
    st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)

