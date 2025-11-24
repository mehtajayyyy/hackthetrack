"""
Data Tab Module
===============
Displays data upload and inspection functionality.
"""

import pandas as pd
import streamlit as st

from data_processing import list_sheets
from ui_components import section


def render_data_tab(file_source: str, sheets: list):
    """
    Render the Data tab with file upload and inspection.
    
    Args:
        file_source: Path to the current dataset file
        sheets: List of available sheets in the dataset
    """
    section("Upload / Inspect")
    up1 = st.file_uploader(
        "Upload timing/telemetry CSV", 
        type=["csv"], 
        key="data_upload"
    )
    if up1:
        try:
            user_df = pd.read_csv(up1)
            st.success(f"Loaded {user_df.shape[0]} rows × {user_df.shape[1]} cols")
            st.dataframe(user_df.head(100), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to parse file: {e}")

    st.caption(f"Current dataset: {file_source}")
    st.caption(
        f"Available sheets: {', '.join(sheets[:10])}{'...' if len(sheets) > 10 else ''}"
    )

