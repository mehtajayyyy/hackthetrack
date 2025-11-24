"""
Telemetry Processing Module
============================
Handles loading and processing of telemetry data from CSV or aggregated Parquet files.
"""

import os
import pandas as pd
import streamlit as st
from typing import Dict, Tuple, Optional

from config import (
    ID_COL, 
    LAP_COL, 
    TELEMETRY_R1_PATH, 
    TELEMETRY_R2_PATH,
    TELEMETRY_R1_AGGREGATED_PATH,
    TELEMETRY_R2_AGGREGATED_PATH,
    USE_AGGREGATED_TELEMETRY
)


@st.cache_data(show_spinner=False)
def load_telemetry(race: str) -> pd.DataFrame:
    """
    Load telemetry data from aggregated Parquet files (preferred) or CSV files (fallback).
    
    The function first checks for pre-aggregated Parquet files which are much smaller
    (~50-100MB vs 1.5GB). If not found, it falls back to raw CSV files.
    
    Args:
        race: "Race 1" or "Race 2"
        
    Returns:
        DataFrame with telemetry data, empty DataFrame if error
    """
    try:
        # Determine file paths based on race
        if race == "Race 1":
            aggregated_file = TELEMETRY_R1_AGGREGATED_PATH
            csv_file = TELEMETRY_R1_PATH
        else:
            aggregated_file = TELEMETRY_R2_AGGREGATED_PATH
            csv_file = TELEMETRY_R2_PATH
        
        # Try to load aggregated Parquet file first (if enabled and exists)
        if USE_AGGREGATED_TELEMETRY and os.path.exists(aggregated_file):
            try:
                df = pd.read_parquet(aggregated_file)
                # The aggregated file is already in pivot format, so we need to
                # convert it back to long format for compatibility with process_telemetry
                # But actually, process_telemetry expects the long format, so we need
                # to handle this differently. Let's check the structure first.
                
                # If the file has vehicle_id and lap columns, it's already aggregated
                # We'll return it as-is and process_telemetry will handle it
                return df
            except Exception as e:
                # If Parquet loading fails, fall back to CSV
                pass
        
        # Fallback to CSV file (for local development or if aggregated not available)
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, low_memory=False)
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Convert telemetry_value to numeric
            if 'telemetry_value' in df.columns:
                df['telemetry_value'] = pd.to_numeric(df['telemetry_value'], errors='coerce')
            
            return df
        else:
            # Neither file exists
            return pd.DataFrame()
            
    except Exception as e:
        return pd.DataFrame()


def process_telemetry(
    telemetry_df: pd.DataFrame, 
    vehicle_id: Optional[str] = None, 
    lap_range: Optional[Tuple[int, int]] = None
) -> Tuple[Dict, pd.DataFrame]:
    """
    Process telemetry data to extract key metrics.
    
    Handles both aggregated Parquet format (already pivoted) and raw CSV format (long format).
    
    Args:
        telemetry_df: Telemetry DataFrame (either raw long format or aggregated pivot format)
        vehicle_id: Optional vehicle ID to filter by
        lap_range: Optional tuple (min_lap, max_lap) to filter by
        
    Returns:
        Tuple of (metrics_dict, processed_pivot_dataframe)
    """
    if telemetry_df.empty:
        return {}, pd.DataFrame()
    
    # Check if data is already in pivot format (from aggregated Parquet)
    # Aggregated format has vehicle_id, lap, and telemetry_name columns as separate columns
    # Raw format has vehicle_id, lap, telemetry_name, telemetry_value columns
    is_pivot_format = 'telemetry_name' not in telemetry_df.columns or 'telemetry_value' not in telemetry_df.columns
    
    if is_pivot_format:
        # Data is already aggregated (from Parquet file)
        # Filter by vehicle if specified
        if vehicle_id is not None:
            telemetry_df = telemetry_df[telemetry_df[ID_COL] == str(vehicle_id)]
        
        # Filter by lap range if specified
        if lap_range is not None:
            min_lap, max_lap = lap_range
            telemetry_df = telemetry_df[
                (telemetry_df[LAP_COL] >= min_lap) & 
                (telemetry_df[LAP_COL] <= max_lap)
            ]
        
        if telemetry_df.empty:
            return {}, pd.DataFrame()
        
        # Data is already in pivot format, use it directly
        telemetry_pivot = telemetry_df.copy()
    else:
        # Data is in long format (from CSV file)
        # Filter by vehicle if specified
        if vehicle_id is not None:
            telemetry_df = telemetry_df[telemetry_df[ID_COL] == str(vehicle_id)]
        
        # Filter by lap range if specified
        if lap_range is not None:
            min_lap, max_lap = lap_range
            telemetry_df = telemetry_df[
                (telemetry_df[LAP_COL] >= min_lap) & 
                (telemetry_df[LAP_COL] <= max_lap)
            ]
        
        if telemetry_df.empty:
            return {}, pd.DataFrame()
        
        # Pivot telemetry data - aggregate by vehicle and lap first
        try:
            telemetry_pivot = telemetry_df.pivot_table(
                index=[ID_COL, LAP_COL],
                columns='telemetry_name',
                values='telemetry_value',
                aggfunc='mean'
            ).reset_index()
        except Exception:
            return {}, pd.DataFrame()
    
    metrics = {}
    
    # Extract speed
    if 'speed' in telemetry_pivot.columns:
        metrics['speed'] = telemetry_pivot.set_index([ID_COL, LAP_COL])['speed']
    
    # Extract fuel (estimate from throttle/brake usage)
    if 'aps' in telemetry_pivot.columns:  # Accelerator pedal sensor
        metrics['fuel_usage'] = telemetry_pivot.set_index([ID_COL, LAP_COL])['aps']
    
    # Extract tyre wear indicators (from brake pressure and acceleration)
    brake_cols = [c for c in telemetry_pivot.columns if 'pbrake' in str(c).lower()]
    if brake_cols:
        metrics['brake_usage'] = telemetry_pivot.set_index([ID_COL, LAP_COL])[brake_cols[0]]
    
    # Extract acceleration data
    if 'accx_can' in telemetry_pivot.columns:
        metrics['acceleration'] = telemetry_pivot.set_index([ID_COL, LAP_COL])['accx_can']
    
    # Extract gear data
    if 'gear' in telemetry_pivot.columns:
        metrics['gear'] = telemetry_pivot.set_index([ID_COL, LAP_COL])['gear']
    
    # Extract engine RPM
    if 'nmot' in telemetry_pivot.columns:
        metrics['rpm'] = telemetry_pivot.set_index([ID_COL, LAP_COL])['nmot']
    
    return metrics, telemetry_pivot

