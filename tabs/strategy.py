"""
Strategy Tab Module
===================
Displays live pace analysis, replay functionality, and leaderboard.
"""

import pandas as pd
import streamlit as st

from config import ID_COL, LAP_COL
from data_processing import build_laps, rolling_consistency, best_lap
from ui_components import section


def render_strategy_tab(file_source: str):
    """
    Render the Strategy tab with live pace and replay analysis.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    section("Live Pace & Replay", "Simulate race progress and analyze pace")
    
    race_strategy = st.session_state.selected_race
    vehicle_strategy = st.session_state.selected_vehicle
    current_lap_strategy = st.session_state.current_lap_filter
    
    laps_strategy = build_laps(file_source, race_strategy)
    
    if laps_strategy.empty:
        st.error("No lap data could be computed (missing timestamps).")
    else:
        # Filter by vehicle if selected
        if vehicle_strategy:
            laps_strategy = laps_strategy[laps_strategy[ID_COL] == vehicle_strategy].copy()
        
        max_lap = int(laps_strategy[LAP_COL].max())
        progress = st.slider(
            "Replay progress (lap)", 
            1, 
            max_lap, 
            value=min(current_lap_strategy if current_lap_strategy else 10, max_lap),
            key="strategy_progress"
        )
        live = laps_strategy[laps_strategy[LAP_COL] <= progress].copy()

        # Rolling pace & consistency
        win = st.slider("Rolling window (laps)", 3, 10, 5, key="strategy_window")
        live["pace_s"] = live.groupby(ID_COL)["lap_time_s"].transform(
            lambda s: s.rolling(win, min_periods=1).mean()
        )
        live["consistency_std"] = live.groupby(ID_COL)["lap_time_s"].transform(
            lambda s: rolling_consistency(s, window=max(win, 6))
        )

        # Leaderboard
        rs = (live.assign(lap_time_s_clean=lambda d: d["lap_time_s"].fillna(d["pace_s"]))
                    .groupby(ID_COL)
                    .agg(
                        laps_done=(LAP_COL, "max"),
                        est_cum_time_s=("lap_time_s_clean", "sum"),
                        current_pace_s=("pace_s", "last"),
                        best_lap_s=("lap_time_s", "min"),
                        consistency_std=("consistency_std", "last")
                    )
                    .sort_values("est_cum_time_s")
                    .reset_index()
        )
        
        st.markdown("#### Leaderboard")
        st.dataframe(rs, use_container_width=True, hide_index=True)
        
        # Race leader metrics
        if len(rs):
            top = rs.iloc[0]
            st.markdown("#### Race Leader")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Laps Done", int(top["laps_done"]))
            with c2:
                if pd.notna(top["current_pace_s"]):
                    st.metric("Current Pace", f"{float(top['current_pace_s']):.2f}s")
            with c3:
                if pd.notna(top["best_lap_s"]):
                    st.metric("Best Lap", f"{float(top['best_lap_s']):.2f}s")

