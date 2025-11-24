"""
Configuration Module for RaceIQ Pro
====================================
Contains all constants, sheet names, and column mappings used throughout the application.
"""

# =========================
# Sheet Names Mapping
# =========================
SHEET_NAMES = {
    "R1_end": "R1_barber_lap_end",
    "R2_end": "R2_barber_lap_end",
    "R1_time": "R1_barber_lap_time",
    "R2_time": "R2_barber_lap_time",
    "W1": "26_Weather_Race 1_Anonymized",
    "W2": "26_Weather_Race 2_Anonymized",
    "SEC_R2": "23_AnalysisEnduranceWithSection",
    "RESULTS_R1": "05_Provisional Results by Class_Race 1_Anonymized",
    "RESULTS_R2": "05_Provisional Results by Class_Race 2_Anonymized",
}

# =========================
# Column Names
# =========================
ID_COL = "vehicle_id"
LAP_COL = "lap"
TIME_COLS_END = ["timestamp", "meta_time"]  # Choose first present
TIME_COLS_TIME = ["timestamp"]

# =========================
# Data File Paths
# =========================
DEFAULT_DATASET_PATH = "Toyota GR Hackathon Datasets.xlsx"
TELEMETRY_R1_PATH = "R1_barber_telemetry_data.csv"
TELEMETRY_R2_PATH = "R2_barber_telemetry_data.csv"

# Aggregated telemetry files (pre-processed, much smaller)
TELEMETRY_R1_AGGREGATED_PATH = "R1_barber_telemetry_aggregated.parquet"
TELEMETRY_R2_AGGREGATED_PATH = "R2_barber_telemetry_aggregated.parquet"

# Configuration flag for using aggregated data
USE_AGGREGATED_TELEMETRY = True  # Set to False to use raw CSV files

# =========================
# Theme Colors
# =========================
PRIMARY = "#0F62FE"   # IBM blue
ACCENT = "#24A148"    # green
WARNING = "#FF832B"   # orange
DANGER = "#DA1E28"    # red
MUTED = "#697077"     # gray

# =========================
# App Configuration
# =========================
APP_TITLE = "RaceIQ Pro – Real‑Time Strategy Console"
APP_ICON = "🏁"
BRAND_NAME = "RaceIQ Pro"
BRAND_TAGLINE = "AI Race Strategist"

# =========================
# Live Mode Configuration
# =========================
LIVE_MODE_UPDATE_INTERVAL = 5  # seconds
DEFAULT_START_LAP = 5

