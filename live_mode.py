"""
Live Mode Module
================
Handles auto-refresh logic for live mode functionality.
"""

import time
import streamlit as st

from config import ID_COL, LAP_COL, LIVE_MODE_UPDATE_INTERVAL
from data_processing import build_laps


def handle_live_mode(file_source: str):
    """
    Handle live mode auto-refresh logic.
    Only runs when live mode is explicitly enabled.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    # Only run auto-refresh if live mode is explicitly ON
    # Use explicit boolean check to ensure it's truly on
    lap_live_state = st.session_state.get('lap_live', False)

    # Explicitly check if live mode is ON (must be True, not just truthy)
    if lap_live_state is True:  # Only proceed if live mode is explicitly ON
        current_time = time.time()
        
        # Initialize if not set
        if 'last_lap_update' not in st.session_state:
            st.session_state.last_lap_update = current_time
            st.session_state.current_lap_filter = 1
        
        last_update = st.session_state.get('last_lap_update', current_time)
        time_since_update = current_time - last_update
        
        # Get max lap for current race
        race_for_live = st.session_state.get('selected_race', 'Race 1')
        laps_for_live = build_laps(file_source, race_for_live)
        max_lap_live = (
            int(laps_for_live[LAP_COL].max()) 
            if not laps_for_live.empty 
            else 28
        )
        
        # Update every 5.5 seconds
        if time_since_update >= LIVE_MODE_UPDATE_INTERVAL:
            current_lap_value = st.session_state.get('current_lap_filter', 1)
            
            if current_lap_value < max_lap_live:
                st.session_state.current_lap_filter = current_lap_value + 1
            else:
                # Reached max lap - keep at max
                st.session_state.current_lap_filter = max_lap_live
            
            st.session_state.last_lap_update = current_time
            # Small delay to prevent too rapid reruns
            time.sleep(0.3)
            st.rerun()  # Trigger rerun to update display
        else:
            # Not time yet - wait and rerun to check again
            # Check every 1 second to be responsive
            wait_time = min(1.0, max(0.5, LIVE_MODE_UPDATE_INTERVAL - time_since_update))
            time.sleep(wait_time)
            st.rerun()  # Rerun to check again
    # Live mode is OFF - do nothing, no auto-refresh, no reruns

