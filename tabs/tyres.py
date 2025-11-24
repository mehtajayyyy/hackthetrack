"""
Tyres Tab Module
================
Displays tyre health, consistency analysis, and best lap statistics.
"""

import numpy as np
import pandas as pd
import streamlit as st

from config import ID_COL, LAP_COL
from data_processing import build_laps
from telemetry import load_telemetry, process_telemetry
from ui_components import section


def render_tyres_tab(file_source: str):
    """
    Render the Tyres tab with tyre health and consistency analysis.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    section("Tyre Health & Consistency", "Wear, deg and temperature windows")
    
    race_tyres = st.session_state.selected_race
    vehicle_tyres = st.session_state.selected_vehicle
    current_lap_tyres = st.session_state.current_lap_filter
    
    laps_tyres = build_laps(file_source, race_tyres)
    telemetry_tyres = load_telemetry(race_tyres)
    
    if laps_tyres.empty:
        st.info("No lap data available.")
    else:
        # Use vehicle from sidebar (no separate selector)
        if vehicle_tyres:
            st.info(f"📊 Analyzing vehicle: **{vehicle_tyres}** (selected in sidebar)")
        
        # Filter data using sidebar selection
        if vehicle_tyres:
            laps_filtered_tyres = laps_tyres[laps_tyres[ID_COL] == vehicle_tyres].copy()
        else:
            laps_filtered_tyres = laps_tyres.copy()
        
        if current_lap_tyres:
            laps_filtered_tyres = laps_filtered_tyres[
                laps_filtered_tyres[LAP_COL] <= current_lap_tyres
            ]
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Tyre Life Trend")
            if not telemetry_tyres.empty:
                # Process telemetry for tyre analysis
                telemetry_metrics_tyres, _ = process_telemetry(
                    telemetry_tyres,
                    vehicle_id=vehicle_tyres,
                    lap_range=(1, current_lap_tyres) if current_lap_tyres else None
                )
                
                # Calculate tyre life from brake usage and lap data
                if not laps_filtered_tyres.empty:
                    tyre_life_data = []
                    for lap in sorted(laps_filtered_tyres[LAP_COL].unique()):
                        lap_data = laps_filtered_tyres[laps_filtered_tyres[LAP_COL] == lap]
                        if 'brake_usage' in telemetry_metrics_tyres:
                            brake_vals = telemetry_metrics_tyres['brake_usage']
                            if lap in brake_vals.index.get_level_values(LAP_COL):
                                brake_usage = brake_vals.xs(lap, level=LAP_COL).mean()
                            else:
                                brake_usage = 50  # Default
                        else:
                            brake_usage = 50
                        
                        # Estimate tyre life: 100% - (lap * wear_rate * brake_factor)
                        wear_rate = 0.3
                        brake_factor = 1 + (brake_usage / 200)  # More brake = more wear
                        tyre_life = max(0, 100 - (lap * wear_rate * brake_factor))
                        tyre_life_data.append({"Lap": lap, "Tyre Life": tyre_life})
                    
                    if tyre_life_data:
                        tyre_df = pd.DataFrame(tyre_life_data).set_index("Lap")
                        st.line_chart(tyre_df, height=260)
                    else:
                        # Fallback
                        tyre_data = laps_filtered_tyres.groupby(LAP_COL)["lap_time_s"].mean().reset_index()
                        tyre_data["tyre_life"] = 100 - (tyre_data[LAP_COL] * 0.3)
                        st.line_chart(tyre_data.set_index(LAP_COL)[["tyre_life"]], height=260)
                else:
                    st.info("No data for selected filters")
            else:
                # Fallback to estimated data
                tyre_data = laps_filtered_tyres.groupby(LAP_COL)["lap_time_s"].mean().reset_index()
                tyre_data["tyre_life"] = 100 - (tyre_data[LAP_COL] * 0.3)
                st.line_chart(tyre_data.set_index(LAP_COL)[["tyre_life"]], height=260)
        
        with c2:
            st.markdown("#### Compound Comparison")
            compound_data = pd.DataFrame({
                "Compound": ["S", "M", "H"],
                "Life (laps)": [8, 22, 30],
                "Delta (s/lap)": [-0.8, 0.0, +0.5],
                "Window": ["85–100°C", "80–95°C", "75–90°C"]
            })
            st.dataframe(compound_data, use_container_width=True, hide_index=True)
        
        st.markdown("#### Driver Performance Statistics")
        # Per-driver stats
        stats = (laps_filtered_tyres.groupby(ID_COL)
                      .agg(
                          best_lap_s=("lap_time_s", "min"),
                          mean_lap_s=("lap_time_s", "mean"),
                          laps=("lap", "count")
                      )
                      .reset_index()
        )
        stats["consistency_std"] = (
            laps_filtered_tyres.groupby(ID_COL)["lap_time_s"]
            .apply(lambda s: np.nanstd(s.values))
            .reindex(stats[ID_COL])
            .values
        )
        
        st.dataframe(
            stats.sort_values("best_lap_s").reset_index(drop=True), 
            use_container_width=True, 
            hide_index=True
        )
        
        st.markdown("#### Best Lap Distribution")
        try:
            st.bar_chart(stats.set_index(ID_COL)["best_lap_s"], height=300)
        except Exception:
            pass

