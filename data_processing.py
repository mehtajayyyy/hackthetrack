"""
Data Processing Module
======================
Handles all data loading, processing, and transformation operations.
"""

import pandas as pd
import numpy as np
from typing import Optional

from config import (
    SHEET_NAMES, ID_COL, LAP_COL, TIME_COLS_END, TIME_COLS_TIME
)


def list_sheets(file_or_buffer: str) -> list:
    """
    List all sheet names in an Excel file.
    
    Args:
        file_or_buffer: Path to Excel file or file buffer
        
    Returns:
        List of sheet names, empty list if error
    """
    try:
        return pd.ExcelFile(file_or_buffer).sheet_names
    except Exception:
        return []


def read_sheet(file_or_buffer: str, sheet: str) -> Optional[pd.DataFrame]:
    """
    Read a specific sheet from an Excel file.
    
    Args:
        file_or_buffer: Path to Excel file or file buffer
        sheet: Name of the sheet to read
        
    Returns:
        DataFrame if successful, None otherwise
    """
    try:
        return pd.read_excel(file_or_buffer, sheet_name=sheet)
    except Exception:
        return None


def to_dt(s) -> pd.Series:
    """
    Convert series to datetime with multiple fallback strategies.
    
    Args:
        s: Series or scalar to convert
        
    Returns:
        Series of datetime objects or NaT if conversion fails
    """
    try:
        return pd.to_datetime(s, errors="coerce", utc=True)
    except Exception:
        try:
            return pd.to_datetime(s, errors="coerce")
        except Exception:
            if isinstance(s, pd.Series):
                return pd.Series([pd.NaT] * len(s))
            return pd.NaT


def compute_lap_time_from_timestamps(
    df: pd.DataFrame, 
    id_col: str, 
    lap_col: str, 
    time_cols: list
) -> pd.DataFrame:
    """
    Compute lap times from timestamp differences.
    
    Args:
        df: DataFrame with lap data
        id_col: Column name for vehicle ID
        lap_col: Column name for lap number
        time_cols: List of possible timestamp column names
        
    Returns:
        DataFrame with vehicle_id, lap, and lap_time_s columns
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[id_col, lap_col, "lap_time_s"])

    base = df.copy()
    if id_col not in base.columns or lap_col not in base.columns:
        return pd.DataFrame(columns=[id_col, lap_col, "lap_time_s"])

    # Pick a timestamp column
    ts_col = None
    for c in time_cols:
        if c in base.columns:
            ts_col = c
            break
    if ts_col is None:
        return pd.DataFrame(columns=[id_col, lap_col, "lap_time_s"])

    base[id_col] = base[id_col].astype(str)
    base[lap_col] = pd.to_numeric(base[lap_col], errors="coerce").astype("Int64")
    base["__ts__"] = to_dt(base[ts_col])

    def per_id(g):
        """Calculate lap times per vehicle."""
        # Sort by LAP then timestamp; diff to get lap duration
        g = g.sort_values([lap_col, "__ts__"])
        g["lap_time_s"] = g["__ts__"].diff().dt.total_seconds()
        return g[[id_col, lap_col, "lap_time_s"]]

    out = base.groupby(id_col, group_keys=False).apply(per_id)
    out = out.drop_duplicates(subset=[id_col, lap_col], keep="last").reset_index(drop=True)
    return out


def build_laps(file_or_buffer: str, race: str) -> pd.DataFrame:
    """
    Build lap data for the selected race by merging end and time sheets.
    
    Args:
        file_or_buffer: Path to Excel file or file buffer
        race: "Race 1" or "Race 2"
        
    Returns:
        DataFrame with lap data including lap_time_s
    """
    if race == "Race 1":
        end_sheet, time_sheet = SHEET_NAMES["R1_end"], SHEET_NAMES["R1_time"]
    else:
        end_sheet, time_sheet = SHEET_NAMES["R2_end"], SHEET_NAMES["R2_time"]

    end_df = read_sheet(file_or_buffer, end_sheet)
    time_df = read_sheet(file_or_buffer, time_sheet)

    end_laps = compute_lap_time_from_timestamps(
        end_df, ID_COL, LAP_COL, TIME_COLS_END
    )
    time_laps = compute_lap_time_from_timestamps(
        time_df, ID_COL, LAP_COL, TIME_COLS_TIME
    )

    if not time_laps.empty:
        merged = pd.merge(
            end_laps[[ID_COL, LAP_COL]], 
            time_laps, 
            on=[ID_COL, LAP_COL], 
            how="outer"
        )
    else:
        merged = end_laps

    if not merged.empty:
        merged[ID_COL] = merged[ID_COL].astype(str)
        merged[LAP_COL] = pd.to_numeric(merged[LAP_COL], errors="coerce").astype("Int64")
        merged = merged.dropna(subset=[LAP_COL]).sort_values([ID_COL, LAP_COL]).reset_index(drop=True)
    
    return merged


def rolling_consistency(x: pd.Series, window: int = 8) -> pd.Series:
    """
    Calculate rolling consistency using Median Absolute Deviation.
    
    Args:
        x: Series of lap times
        window: Rolling window size
        
    Returns:
        Series of consistency values (robust standard deviation)
    """
    med = x.rolling(window, min_periods=3).median()
    mad = (x - med).abs().rolling(window, min_periods=3).median()
    return 1.4826 * mad


def best_lap(df: pd.DataFrame) -> float:
    """
    Get the best (minimum) lap time from a DataFrame.
    
    Args:
        df: DataFrame with lap_time_s column
        
    Returns:
        Minimum lap time in seconds, or NaN if no data
    """
    s = df["lap_time_s"]
    return float(np.nanmin(s)) if len(s) else np.nan

