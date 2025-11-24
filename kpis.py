"""
KPIs Module
===========
Calculates and displays key performance indicators.
"""

import numpy as np
import pandas as pd
import streamlit as st

from config import ID_COL, LAP_COL, PRIMARY
from data_processing import build_laps
from telemetry import load_telemetry, process_telemetry
from ui_components import kpi, render_vehicle_banner


def calculate_kpis(file_source: str):
    """
    Calculate and display all KPIs based on current filters.
    
    Args:
        file_source: Path to the Excel dataset file
    """
    race = st.session_state.selected_race
    selected_vehicle = st.session_state.selected_vehicle
    current_lap = st.session_state.current_lap_filter

    laps = build_laps(file_source, race)

    # Load telemetry data
    telemetry_df = load_telemetry(race)

    # Filter laps by vehicle if selected
    if not laps.empty and selected_vehicle:
        laps_filtered = laps[laps[ID_COL] == selected_vehicle].copy()
    else:
        laps_filtered = laps.copy()

    # Filter by current lap
    if not laps_filtered.empty and current_lap:
        laps_filtered = laps_filtered[laps_filtered[LAP_COL] <= current_lap].copy()

    if not laps_filtered.empty:
        # Calculate current metrics
        total_cars = laps[ID_COL].nunique()  # Total in race
        total_laps = int(laps[LAP_COL].max())  # Max lap in race
        # Start from lap 1, use current_lap if set, otherwise use 1
        current_lap_display = current_lap if current_lap and current_lap >= 1 else 1
        
        # Calculate gap to leader
        if selected_vehicle:
            # For specific vehicle, compare to leader
            vehicle_laps = laps_filtered[laps_filtered[ID_COL] == selected_vehicle]
            if not vehicle_laps.empty:
                vehicle_best = vehicle_laps["lap_time_s"].min()
                all_best = laps.groupby(ID_COL)["lap_time_s"].min()
                leader_best = all_best.min()
                gap_to_lead = (
                    vehicle_best - leader_best 
                    if pd.notna(vehicle_best) and pd.notna(leader_best) 
                    else np.nan
                )
            else:
                gap_to_lead = np.nan
        else:
            # For all vehicles, show average gap
            best_laps = laps_filtered.groupby(ID_COL)["lap_time_s"].min()
            if len(best_laps) > 0:
                leader_best = best_laps.min()
                avg_best = best_laps.mean()
                gap_to_lead = (
                    avg_best - leader_best 
                    if pd.notna(leader_best) and pd.notna(avg_best) 
                    else np.nan
                )
            else:
                gap_to_lead = np.nan
        
        # Calculate fuel from telemetry
        fuel_estimate = None
        if not telemetry_df.empty:
            telemetry_metrics, _ = process_telemetry(
                telemetry_df, 
                vehicle_id=selected_vehicle,
                lap_range=(1, current_lap_display) if current_lap_display else None
            )
            
            # Estimate fuel from throttle usage (aps = accelerator pedal sensor)
            if 'fuel_usage' in telemetry_metrics:
                fuel_data = telemetry_metrics['fuel_usage']
                if not fuel_data.empty:
                    # Normalize throttle usage to estimate fuel consumption
                    # Higher throttle = more fuel consumption
                    avg_throttle = (
                        fuel_data.mean() 
                        if hasattr(fuel_data, 'mean') 
                        else fuel_data
                    )
                    # Estimate: 100L start, ~0.5L per lap at 50% throttle average
                    fuel_estimate = max(
                        0, 
                        100 - (
                            current_lap_display * 0.5 * (
                                avg_throttle / 100 
                                if pd.notna(avg_throttle) 
                                else 0.5
                            )
                        )
                    )
            
            if fuel_estimate is None:
                # Fallback estimate
                fuel_estimate = max(0, 100 - (current_lap_display * 0.5))
        else:
            fuel_estimate = max(0, 100 - (current_lap_display * 0.5))
        
        # Calculate tyre life from telemetry
        tyre_life = None
        if not telemetry_df.empty:
            telemetry_metrics, _ = process_telemetry(
                telemetry_df,
                vehicle_id=selected_vehicle,
                lap_range=(1, current_lap_display) if current_lap_display else None
            )
            
            # Estimate tyre wear from brake usage and acceleration
            if 'brake_usage' in telemetry_metrics:
                brake_data = telemetry_metrics['brake_usage']
                if not brake_data.empty:
                    avg_brake = (
                        brake_data.mean() 
                        if hasattr(brake_data, 'mean') 
                        else brake_data
                    )
                    # Higher brake usage = more tyre wear
                    # Estimate: 100% start, ~0.3% per lap at normal usage
                    brake_factor = (avg_brake / 100) if pd.notna(avg_brake) else 1.0
                    tyre_life = max(0, 100 - (current_lap_display * 0.3 * brake_factor))
            
            if tyre_life is None:
                # Fallback estimate
                tyre_life = max(0, 100 - (current_lap_display * 0.3))
        else:
            tyre_life = max(0, 100 - (current_lap_display * 0.3))
        
        # Display vehicle info if selected
        if selected_vehicle:
            render_vehicle_banner(selected_vehicle, race, current_lap_display, total_laps)
        
        # Display KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            vehicle_label = f" (V:{selected_vehicle})" if selected_vehicle else ""
            kpi(
                "Current Lap", 
                str(current_lap_display), 
                f"On target{vehicle_label}" if current_lap_display > 0 else None, 
                "b-ok"
            )
        with c2: 
            gap_str = f"{gap_to_lead:.1f}s" if pd.notna(gap_to_lead) else "N/A"
            gap_delta = "↓ 0.3s" if pd.notna(gap_to_lead) and gap_to_lead < 0.5 else None
            kpi("Gap to Lead", gap_str, gap_delta, "b-ok")
        with c3: 
            fuel_warning = fuel_estimate < 20
            kpi(
                "Fuel @ Lap End", 
                f"{fuel_estimate:.1f} L", 
                "Risk" if fuel_warning else None, 
                "b-warn" if fuel_warning else "b-ok"
            )
        with c4: 
            pit_lap = (
                int(current_lap_display + (tyre_life / 0.3)) 
                if tyre_life < 50 and tyre_life > 0 
                else None
            )
            pit_text = f"Plan Pit L{pit_lap}" if pit_lap else None
            tyre_warning = tyre_life < 50
            kpi(
                "Tyre Life", 
                f"{tyre_life:.0f}%", 
                pit_text, 
                "b-warn" if tyre_warning else "b-ok"
            )
    else:
        st.info("No data available. Please check race selection and filters.")
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            kpi("Current Lap", "N/A", None, "b-ok")
        with c2: 
            kpi("Gap to Lead", "N/A", None, "b-ok")
        with c3: 
            kpi("Fuel @ Lap End", "N/A", None, "b-warn")
        with c4: 
            kpi("Tyre Life", "N/A", None, "b-warn")

