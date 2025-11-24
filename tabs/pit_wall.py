"""
Pit Wall Tab Module
===================
Displays pit window analysis, undercut opportunities, and strategy advisor.
"""

import pandas as pd
import streamlit as st

from config import ID_COL, LAP_COL
from data_processing import build_laps
from ui_components import section


def render_pit_wall_tab(file_source: str):
    """
    Render the Pit Wall tab with undercut and pit window analysis.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    section("Pit Window & Box Calls", "Manage windows, deltas and safety car options")
    
    race_pit = st.session_state.selected_race
    vehicle_pit = st.session_state.selected_vehicle
    current_lap_pit = st.session_state.current_lap_filter
    
    laps_pit = build_laps(file_source, race_pit)
    
    if laps_pit.empty:
        st.error("No lap data available.")
    else:
        # Filter by vehicle if selected (but allow comparison, so don't filter too early)
        max_lap = int(laps_pit[LAP_COL].max())
        progress = st.slider(
            "Replay progress (lap)", 
            1, 
            max_lap, 
            value=min(current_lap_pit if current_lap_pit else 10, max_lap),
            key="pit_progress"
        )
        live = laps_pit[laps_pit[LAP_COL] <= progress].copy()

        vids = sorted(live[ID_COL].unique().tolist())
        if len(vids) < 2:
            st.info("Need at least two vehicles in current slice.")
        else:
            c1, c2 = st.columns(2)
            your = c1.selectbox(
                "Your vehicle_id", 
                vids, 
                index=0, 
                key="pit_your"
            )
            rival = c2.selectbox(
                "Rival vehicle_id", 
                [v for v in vids if v != your], 
                index=0, 
                key="pit_rival"
            )

            g = live.pivot_table(
                index=LAP_COL, 
                columns=ID_COL, 
                values="lap_time_s"
            )
            win = st.slider("Delta window (laps)", 3, 10, 5, key="pit_win")
            roll = g.rolling(win, min_periods=1).mean()

            if your in roll.columns and rival in roll.columns:
                st.line_chart(
                    roll[[your, rival]].rename(
                        columns={your: "you_pace_s", rival: "rival_pace_s"}
                    ), 
                    height=240
                )
                delta = roll[your] - roll[rival]
                st.line_chart(delta.rename("delta_vs_rival_s"), height=160)
                st.line_chart(delta.cumsum().rename("cumulative_delta_s"), height=160)
                last_vals = delta.tail(3).mean()
                suggestion = (
                    "Consider undercut" 
                    if pd.notna(last_vals) and last_vals > 0.3 
                    else "Stay out"
                )
                
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1: 
                    st.info(f"Next Box: Lap {progress + 5} ±1", icon="🛑")
                with c2: 
                    st.warning("SC Risk: Medium", icon="⚠️")
                with c3: 
                    delta_str = (
                        f"+{last_vals:.1f}s" 
                        if pd.notna(last_vals) and last_vals > 0 
                        else f"{last_vals:.1f}s"
                    )
                    st.success(f"Undercut: {delta_str} vs Fwd", icon="⚡")
                
                d1, d2 = st.columns(2)
                d1.metric("Strategy Advisor", suggestion)
                d2.metric(
                    "Last 3 Lap Avg Delta", 
                    f"{float(last_vals):.2f}s" if pd.notna(last_vals) else "—"
                )
                
                st.markdown("#### Box Readiness")
                tyre_deg = int(82 - (progress * 0.5))
                fuel_bal = int(64 - (progress * 0.3))
                st.progress(min(100, max(0, tyre_deg)), text="Tyre deg vs plan")
                st.progress(min(100, max(0, fuel_bal)), text="Fuel balance vs plan")
            else:
                st.warning("Selected cars not present in current slice.")

