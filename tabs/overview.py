"""
Overview Tab Module
===================
Displays track telemetry, lap trends, and overall race overview.
"""

import pandas as pd
import streamlit as st

from config import ID_COL, LAP_COL, SHEET_NAMES
from data_processing import build_laps, read_sheet
from telemetry import load_telemetry, process_telemetry
from ui_components import section


def render_overview_tab(file_source: str):
    """
    Render the Overview tab with track telemetry and lap trends.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    section("Track & Telemetry", "Live trends for speed, tyre and fuel")
    
    race_overview = st.session_state.selected_race
    vehicle_overview = st.session_state.selected_vehicle
    current_lap_overview = st.session_state.current_lap_filter
    
    laps_overview = build_laps(file_source, race_overview)
    telemetry_overview = load_telemetry(race_overview)
    
    if laps_overview.empty:
        st.info("No lap data available for this race.")
    else:
        # Filter data
        if vehicle_overview:
            laps_filtered_overview = laps_overview[laps_overview[ID_COL] == vehicle_overview].copy()
        else:
            laps_filtered_overview = laps_overview.copy()
        
        if current_lap_overview:
            laps_filtered_overview = laps_filtered_overview[
                laps_filtered_overview[LAP_COL] <= current_lap_overview
            ]
        
        # Process telemetry if available
        telemetry_metrics_overview = {}
        if not telemetry_overview.empty:
            telemetry_metrics_overview, _ = process_telemetry(
                telemetry_overview,
                vehicle_id=vehicle_overview,
                lap_range=(1, current_lap_overview) if current_lap_overview else None
            )
        
        # Aggregate by lap for charts
        lap_agg = laps_filtered_overview.groupby(LAP_COL).agg({
            "lap_time_s": "mean"
        }).reset_index()
        
        cA, cB = st.columns([2, 1])
        with cA:
            st.markdown("#### Lap Time Trend")
            chart_data = lap_agg.set_index(LAP_COL)[["lap_time_s"]].rename(
                columns={"lap_time_s": "Avg Lap Time (s)"}
            )
            st.line_chart(chart_data, height=240)
            
            # Speed from telemetry if available
            if not telemetry_overview.empty and 'speed' in telemetry_metrics_overview:
                st.markdown("#### Speed Trend (from Telemetry)")
                speed_data = telemetry_metrics_overview['speed']
                if not speed_data.empty:
                    speed_df = speed_data.reset_index()
                    speed_df = speed_df.groupby(LAP_COL)['speed'].mean().reset_index()
                    speed_df = speed_df.set_index(LAP_COL)
                    st.line_chart(speed_df, height=200)
        
        with cB:
            st.markdown("#### Vehicle Distribution")
            if vehicle_overview:
                # Show selected vehicle info
                vehicle_lap_count = len(
                    laps_filtered_overview[laps_filtered_overview[ID_COL] == vehicle_overview]
                )
                st.metric("Selected Vehicle", vehicle_overview)
                st.metric("Laps Recorded", vehicle_lap_count)
                if not laps_filtered_overview.empty:
                    avg_lap_time = laps_filtered_overview[
                        laps_filtered_overview[ID_COL] == vehicle_overview
                    ]["lap_time_s"].mean()
                    st.metric(
                        "Avg Lap Time", 
                        f"{avg_lap_time:.2f}s" if pd.notna(avg_lap_time) else "N/A"
                    )
            else:
                vehicle_counts = laps_filtered_overview[ID_COL].value_counts().head(10)
                if not vehicle_counts.empty:
                    st.bar_chart(vehicle_counts, height=240)
                else:
                    st.info("No data")
        
        cC, cD = st.columns(2)
        with cC:
            st.markdown("#### Fuel Consumption")
            if not telemetry_overview.empty and 'fuel_usage' in telemetry_metrics_overview:
                fuel_vals = telemetry_metrics_overview['fuel_usage']
                if not fuel_vals.empty:
                    fuel_df = fuel_vals.reset_index()
                    value_col = fuel_vals.name if fuel_vals.name else fuel_df.columns[-1]
                    fuel_lap_agg = fuel_df.groupby(LAP_COL)[value_col].mean().reset_index()
                    fuel_lap_agg['fuel_remaining'] = 100 - (
                        fuel_lap_agg[LAP_COL] * 0.5 * (fuel_lap_agg[value_col] / 100)
                    )
                    fuel_chart = fuel_lap_agg.set_index(LAP_COL)[['fuel_remaining']]
                    st.area_chart(fuel_chart, height=220)
                else:
                    fuel_trend = pd.DataFrame({
                        "Lap": lap_agg[LAP_COL],
                        "Fuel": 100 - (lap_agg[LAP_COL] * 0.5)
                    }).set_index("Lap")
                    st.area_chart(fuel_trend, height=220)
            else:
                fuel_trend = pd.DataFrame({
                    "Lap": lap_agg[LAP_COL],
                    "Fuel": 100 - (lap_agg[LAP_COL] * 0.5)
                }).set_index("Lap")
                st.area_chart(fuel_trend, height=220)
        
        with cD:
            st.markdown("#### Tyre Life")
            if not telemetry_overview.empty and 'brake_usage' in telemetry_metrics_overview:
                brake_vals = telemetry_metrics_overview['brake_usage']
                if not brake_vals.empty:
                    brake_df = brake_vals.reset_index()
                    value_col = brake_vals.name if brake_vals.name else brake_df.columns[-1]
                    brake_lap_agg = brake_df.groupby(LAP_COL)[value_col].mean().reset_index()
                    brake_lap_agg['tyre_life'] = 100 - (
                        brake_lap_agg[LAP_COL] * 0.3 * (1 + brake_lap_agg[value_col] / 200)
                    )
                    brake_chart = brake_lap_agg.set_index(LAP_COL)[['tyre_life']]
                    st.area_chart(brake_chart, height=220)
                else:
                    tyre_trend = pd.DataFrame({
                        "Lap": lap_agg[LAP_COL],
                        "Tyre Life": 100 - (lap_agg[LAP_COL] * 0.3)
                    }).set_index("Lap")
                    st.area_chart(tyre_trend, height=220)
            else:
                tyre_trend = pd.DataFrame({
                    "Lap": lap_agg[LAP_COL],
                    "Tyre Life": 100 - (lap_agg[LAP_COL] * 0.3)
                }).set_index("Lap")
                st.area_chart(tyre_trend, height=220)
        
        # Additional telemetry analysis
        if not telemetry_overview.empty:
            st.markdown("#### Additional Telemetry Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'acceleration' in telemetry_metrics_overview:
                    accel_data = telemetry_metrics_overview['acceleration']
                    if not accel_data.empty:
                        st.metric(
                            "Avg Acceleration", 
                            f"{accel_data.mean():.2f} g" if hasattr(accel_data, 'mean') else "N/A"
                        )
            
            with col2:
                if 'rpm' in telemetry_metrics_overview:
                    rpm_data = telemetry_metrics_overview['rpm']
                    if not rpm_data.empty:
                        st.metric(
                            "Avg RPM", 
                            f"{rpm_data.mean():.0f}" if hasattr(rpm_data, 'mean') else "N/A"
                        )
            
            with col3:
                if 'gear' in telemetry_metrics_overview:
                    gear_data = telemetry_metrics_overview['gear']
                    if not gear_data.empty:
                        st.metric(
                            "Avg Gear", 
                            f"{gear_data.mean():.1f}" if hasattr(gear_data, 'mean') else "N/A"
                        )
        
        # Show lap data table
        st.markdown("#### Lap Data")
        st.dataframe(laps_filtered_overview.head(100), use_container_width=True, hide_index=True)
        
        # Optional results sheet
        res_sheet = SHEET_NAMES.get(
            "RESULTS_R1" if race_overview == "Race 1" else "RESULTS_R2"
        )
        results_df = read_sheet(file_source, res_sheet)
        if results_df is not None and not results_df.empty:
            st.markdown("#### Provisional Results")
            st.dataframe(results_df.head(30), use_container_width=True, hide_index=True)

    with st.expander("Session Notes", expanded=False):
        st.text_area(
            "Notes", 
            placeholder="Add decisions, incidents, weather calls…", 
            height=120, 
            key="overview_notes"
        )

