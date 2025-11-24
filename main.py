"""
RaceIQ Pro - Main Application
==============================
Real-Time Race Strategy Analytics Platform

This is the main entry point for the RaceIQ Pro application.
The application is structured in a modular way for easy understanding and maintenance.

Module Structure:
- config.py: Configuration constants and settings
- data_processing.py: Data loading and processing functions
- telemetry.py: Telemetry data processing
- ui_components.py: UI components and styling
- sidebar.py: Sidebar controls and filters
- kpis.py: Key Performance Indicators calculation
- live_mode.py: Live mode auto-refresh logic
- tabs/: Tab modules for different views
    - overview.py: Track telemetry and overview
    - strategy.py: Live pace and replay
    - pit_wall.py: Pit window and undercut analysis
    - tyres.py: Tyre health and consistency
    - fuel.py: Fuel strategy and weather correlation
    - data.py: Data upload and inspection
"""

import streamlit as st

from config import APP_TITLE, APP_ICON, DEFAULT_DATASET_PATH
from data_processing import list_sheets
from ui_components import apply_custom_styles
from sidebar import render_sidebar
from kpis import calculate_kpis
from live_mode import handle_live_mode
from tabs import (
    render_overview_tab,
    render_strategy_tab,
    render_pit_wall_tab,
    render_tyres_tab,
    render_fuel_tab,
    render_data_tab,
)

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Apply Custom Styles
# =========================
apply_custom_styles()

# =========================
# Data Source Setup
# =========================
file_source = DEFAULT_DATASET_PATH
sheets = list_sheets(file_source)
if not sheets:
    st.error("Could not read the workbook.")
    st.stop()

# =========================
# Sidebar - Global Controls
# =========================
render_sidebar(file_source)

# =========================
# Main Content Area
# =========================
# Remove toolbar from main canvas
st.markdown("""
    <style>
        /* Hide toolbar in main canvas */
        .stApp > header {
            visibility: hidden;
            height: 0;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# KPIs Section
# =========================
calculate_kpis(file_source)

st.divider()

# =========================
# Main Tabs
# =========================
tab_overview, tab_strategy, tab_pit, tab_tyres, tab_fuel, tab_data = st.tabs(
    ["🏎️ Overview", "🧭 Strategy", "🛠️ Pit Wall", "🧱 Tyres", "⛽ Fuel", "📁 Data"]
)

with tab_overview:
    render_overview_tab(file_source)

with tab_strategy:
    render_strategy_tab(file_source)

with tab_pit:
    render_pit_wall_tab(file_source)

with tab_tyres:
    render_tyres_tab(file_source)

with tab_fuel:
    render_fuel_tab(file_source)

with tab_data:
    render_data_tab(file_source, sheets)

# =========================
# Live Mode Auto-Refresh
# =========================
handle_live_mode(file_source)

