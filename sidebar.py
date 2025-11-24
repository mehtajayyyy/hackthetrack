"""
Sidebar Module
==============
Handles sidebar controls, filters, and live mode logic.
"""

import time
import streamlit as st

from config import ID_COL, LAP_COL, DEFAULT_START_LAP
from data_processing import build_laps
from ui_components import render_sidebar_branding


def initialize_session_state():
    """Initialize all session state variables."""
    if 'selected_race' not in st.session_state:
        st.session_state.selected_race = "Race 1"
    if 'selected_vehicle' not in st.session_state:
        st.session_state.selected_vehicle = None
    if 'current_lap_filter' not in st.session_state:
        st.session_state.current_lap_filter = DEFAULT_START_LAP
    if 'last_lap_update' not in st.session_state:
        st.session_state.last_lap_update = time.time()
    if 'lap_live' not in st.session_state:
        st.session_state.lap_live = False


def render_sidebar(file_source: str):
    """
    Render the sidebar with all controls and filters.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    with st.sidebar:
        # Branding
        render_sidebar_branding()
        
        st.markdown("### ⚙️ Controls")
        
        # Initialize session state
        initialize_session_state()
        
        # Race selection
        selected_race = st.radio(
            "Select Race",
            ["Race 1", "Race 2"],
            index=0 if st.session_state.selected_race == "Race 1" else 1,
            key="sidebar_race_selector"
        )
        st.session_state.selected_race = selected_race
        
        st.divider()
        
        # Load data for selected race
        laps = build_laps(file_source, selected_race)
        
        if not laps.empty:
            max_lap = int(laps[LAP_COL].max())
            total_cars = laps[ID_COL].nunique()
            vehicles = sorted(laps[ID_COL].unique().tolist())
            
            st.metric("Total Vehicles", total_cars)
            st.metric("Max Laps", max_lap)
            
            st.divider()
            st.markdown("#### Vehicle Filter")
            vehicle_options = ["All Vehicles"] + vehicles
            selected_vehicle_idx = 0
            if (
                st.session_state.selected_vehicle 
                and st.session_state.selected_vehicle in vehicles
            ):
                selected_vehicle_idx = vehicles.index(st.session_state.selected_vehicle) + 1
            
            selected_vehicle_display = st.selectbox(
                "Select Vehicle",
                vehicle_options,
                index=selected_vehicle_idx,
                key="sidebar_vehicle_selector"
            )
            
            if selected_vehicle_display == "All Vehicles":
                st.session_state.selected_vehicle = None
            else:
                st.session_state.selected_vehicle = selected_vehicle_display
            
            st.divider()
            st.markdown("#### Lap Filter")
            
            # Auto-update lap in live mode
            lap_live = st.toggle(
                "Live Mode", 
                value=st.session_state.get('lap_live', False), 
                help="When on, auto-updates lap every 5-6 seconds."
            )
            
            # Store lap_live in session state
            was_live_before = st.session_state.get('lap_live', False)
            st.session_state.lap_live = lap_live
            
            # Initialize/reset when live mode is turned on
            if lap_live:
                if not was_live_before or 'last_lap_update' not in st.session_state:
                    # Just turned on or first time - reset to lap 1
                    st.session_state.last_lap_update = time.time()
                    st.session_state.current_lap_filter = 1  # Start from lap 1
            else:
                # Live mode turned off - clean up auto-refresh state
                if 'last_lap_update' in st.session_state:
                    del st.session_state.last_lap_update
                # Don't auto-increment when live mode is off
            
            current_lap = st.slider(
                "Current Lap",
                1,
                max_lap,
                value=(
                    st.session_state.current_lap_filter 
                    if st.session_state.current_lap_filter 
                    else 1
                ),
                key="sidebar_lap_slider",
                disabled=lap_live  # Disable manual control in live mode
            )
            
            if not lap_live:
                st.session_state.current_lap_filter = current_lap
            
            if lap_live:
                st.info(f"🟢 Live Mode: Lap {st.session_state.current_lap_filter} / {max_lap}")
        else:
            st.session_state.selected_vehicle = None
            st.session_state.current_lap_filter = 1
        
        st.divider()
        st.caption("Tip: Change race/vehicle/lap selection to update all data.")

