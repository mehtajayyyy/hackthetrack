"""
Fuel Tab Module
===============
Displays fuel strategy, consumption trends, and weather correlation.
"""

import numpy as np
import pandas as pd
import streamlit as st

from config import ID_COL, LAP_COL, SHEET_NAMES
from data_processing import build_laps, read_sheet
from telemetry import load_telemetry, process_telemetry
from ui_components import section


def render_fuel_tab(file_source: str):
    """
    Render the Fuel tab with fuel strategy and weather correlation.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    section("Fuel Strategy & Weather Correlation", "Stint burn, mix targets and weather impact")
    
    race_fuel = st.session_state.selected_race
    vehicle_fuel = st.session_state.selected_vehicle
    current_lap_fuel = st.session_state.current_lap_filter
    
    laps_fuel = build_laps(file_source, race_fuel)
    telemetry_fuel = load_telemetry(race_fuel)
    
    if laps_fuel.empty:
        st.info("Need lap data.")
    else:
        # Use vehicle from sidebar (no separate selector)
        if vehicle_fuel:
            st.info(f"📊 Analyzing vehicle: **{vehicle_fuel}** (selected in sidebar)")
        
        # Filter data using sidebar selection
        if vehicle_fuel:
            laps_filtered_fuel = laps_fuel[laps_fuel[ID_COL] == vehicle_fuel].copy()
        else:
            laps_filtered_fuel = laps_fuel.copy()
        
        if current_lap_fuel:
            laps_filtered_fuel = laps_filtered_fuel[
                laps_filtered_fuel[LAP_COL] <= current_lap_fuel
            ]
        
        st.markdown("#### Fuel Consumption Trend")
        if not telemetry_fuel.empty:
            # Process telemetry for fuel analysis
            telemetry_metrics_fuel, _ = process_telemetry(
                telemetry_fuel,
                vehicle_id=vehicle_fuel,
                lap_range=(1, current_lap_fuel) if current_lap_fuel else None
            )
            
            # Calculate fuel from throttle usage
            if not laps_filtered_fuel.empty:
                fuel_data_list = []
                for lap in sorted(laps_filtered_fuel[LAP_COL].unique()):
                    if 'fuel_usage' in telemetry_metrics_fuel:
                        fuel_vals = telemetry_metrics_fuel['fuel_usage']
                        if lap in fuel_vals.index.get_level_values(LAP_COL):
                            throttle_usage = fuel_vals.xs(lap, level=LAP_COL).mean()
                        else:
                            throttle_usage = 50  # Default
                    else:
                        throttle_usage = 50
                    
                    # Estimate fuel: 100L start - (lap * consumption_rate * throttle_factor)
                    consumption_rate = 0.5  # L per lap at 100% throttle
                    throttle_factor = throttle_usage / 100
                    fuel_remaining = max(0, 100 - (lap * consumption_rate * throttle_factor))
                    fuel_data_list.append({"Lap": lap, "Fuel": fuel_remaining})
                
                if fuel_data_list:
                    fuel_df = pd.DataFrame(fuel_data_list).set_index("Lap")
                    st.line_chart(fuel_df, height=260)
                else:
                    # Fallback
                    fuel_data = laps_filtered_fuel.groupby(LAP_COL)["lap_time_s"].mean().reset_index()
                    fuel_data["fuel"] = 100 - (fuel_data[LAP_COL] * 0.5)
                    st.line_chart(fuel_data.set_index(LAP_COL)[["fuel"]], height=260)
            else:
                st.info("No data for selected filters")
        else:
            # Fallback to estimated data
            fuel_data = laps_filtered_fuel.groupby(LAP_COL)["lap_time_s"].mean().reset_index()
            fuel_data["fuel"] = 100 - (fuel_data[LAP_COL] * 0.5)
            st.line_chart(fuel_data.set_index(LAP_COL)[["fuel"]], height=260)
        
        # Weather correlation if available
        st.markdown("#### Weather vs Pace Correlation")
        if race_fuel == "Race 1":
            wx = read_sheet(file_source, SHEET_NAMES["W1"])
        else:
            wx = read_sheet(file_source, SHEET_NAMES["W2"])
        
        if wx is not None and not wx.empty:
            # Use vehicle from sidebar for weather analysis
            if vehicle_fuel:
                vid = vehicle_fuel
            else:
                vids = sorted(laps_filtered_fuel[ID_COL].unique().tolist())
                vid = vids[0] if vids else None
            
            if vid:
                crew = laps_filtered_fuel[laps_filtered_fuel[ID_COL] == vid].copy()
                crew["pace_s"] = crew["lap_time_s"].rolling(5, min_periods=1).mean()
                wx_cols = [
                    c for c in wx.columns 
                    if any(k in str(c).lower() for k in ["temp", "wind", "rain"])
                ]
                if wx_cols:
                    wx_df = wx.reset_index().rename(columns={"index": "wx_idx"})
                    crew = crew.reset_index(drop=True)
                    wx_idx = (
                        np.floor(np.linspace(0, len(wx_df) - 1, len(crew))).astype(int)
                        if len(crew) > 0 
                        else np.array([])
                    )
                    crew["wx_idx"] = wx_idx
                    merged = crew.merge(wx_df, on="wx_idx", how="left")

                    metric = st.selectbox(
                        "Weather metric", 
                        wx_cols, 
                        index=0, 
                        key="fuel_weather"
                    )
                    st.scatter_chart(
                        merged[[metric, "pace_s"]].rename(columns={metric: "weather_metric"}), 
                        height=260
                    )
                    try:
                        corr = merged[metric].corr(merged["pace_s"])
                        c1, c2 = st.columns(2)
                        c1.metric(
                            "Correlation (weather vs pace)", 
                            f"{corr:.3f}" if pd.notna(corr) else "n/a"
                        )
                        c2.metric(
                            "Current rolling pace (s)", 
                            f"{float(crew['pace_s'].iloc[-1]):.2f}"
                        )
                    except Exception:
                        st.metric("Correlation", "n/a")
        
        # Fuel strategy recommendations
        if not laps_filtered_fuel.empty and vehicle_fuel:
            current_fuel = None
            if not telemetry_fuel.empty:
                telemetry_metrics_fuel_check, _ = process_telemetry(
                    telemetry_fuel,
                    vehicle_id=vehicle_fuel,
                    lap_range=(1, current_lap_fuel) if current_lap_fuel else None
                )
                if 'fuel_usage' in telemetry_metrics_fuel_check:
                    fuel_vals = telemetry_metrics_fuel_check['fuel_usage']
                    if not fuel_vals.empty:
                        throttle_usage = (
                            fuel_vals.mean() 
                            if hasattr(fuel_vals, 'mean') 
                            else fuel_vals
                        )
                        current_fuel = max(
                            0, 
                            100 - (
                                current_lap_fuel * 0.5 * (
                                    throttle_usage / 100 
                                    if pd.notna(throttle_usage) 
                                    else 0.5
                                )
                            )
                        )
            
            if current_fuel is None:
                current_fuel = max(0, 100 - (current_lap_fuel * 0.5))
            
            if current_fuel < 30:
                st.markdown(
                    '<span class="badge b-warn">Action</span> Consider short‑fill next stop to avoid traffic.',
                    unsafe_allow_html=True
                )
            elif current_fuel < 50:
                st.markdown(
                    '<span class="badge b-ok">Monitor</span> Fuel levels are moderate. Plan pit stop strategy.',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<span class="badge b-ok">Good</span> Fuel levels are healthy.',
                    unsafe_allow_html=True
                )

