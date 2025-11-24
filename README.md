# RaceIQ Pro - Real-Time Race Strategy Analytics Platform

## Overview

RaceIQ Pro is a comprehensive real-time race strategy analytics platform designed for race engineers and strategists. It provides live telemetry analysis, pit window optimization, fuel strategy planning, and tyre health monitoring.

## Project Structure

The application is organized into a modular structure for easy understanding and maintenance:

```
.
├── main.py                    # Main application entry point
├── config.py                  # Configuration constants and settings
├── data_processing.py          # Data loading and processing functions
├── telemetry.py               # Telemetry data processing
├── ui_components.py           # UI components and styling
├── sidebar.py                 # Sidebar controls and filters
├── kpis.py                    # Key Performance Indicators calculation
├── live_mode.py              # Live mode auto-refresh logic
├── tabs/                      # Tab modules for different views
│   ├── __init__.py
│   ├── overview.py           # Track telemetry and overview
│   ├── strategy.py           # Live pace and replay
│   ├── pit_wall.py            # Pit window and undercut analysis
│   ├── tyres.py               # Tyre health and consistency
│   ├── fuel.py                # Fuel strategy and weather correlation
│   └── data.py                # Data upload and inspection
└── README.md                  # This file
```

## Module Descriptions

### Core Modules

#### `main.py`

- **Purpose**: Main entry point for the Streamlit application
- **Responsibilities**:
  - Page configuration
  - Application initialization
  - Tab orchestration
  - Live mode coordination

#### `config.py`

- **Purpose**: Centralized configuration management
- **Contains**:
  - Sheet name mappings
  - Column name constants
  - Theme colors
  - File paths
  - App configuration settings

#### `data_processing.py`

- **Purpose**: Data loading and transformation
- **Key Functions**:
  - `list_sheets()`: List Excel sheets
  - `read_sheet()`: Read specific Excel sheet
  - `build_laps()`: Build lap data from timestamps
  - `rolling_consistency()`: Calculate rolling consistency
  - `best_lap()`: Get best lap time

#### `telemetry.py`

- **Purpose**: Telemetry data processing
- **Key Functions**:
  - `load_telemetry()`: Load telemetry CSV files
  - `process_telemetry()`: Process and extract telemetry metrics

### UI Modules

#### `ui_components.py`

- **Purpose**: Reusable UI components and styling
- **Key Functions**:
  - `apply_custom_styles()`: Apply custom CSS
  - `kpi()`: Render KPI cards
  - `section()`: Render section headers
  - `render_sidebar_branding()`: Render sidebar branding

#### `sidebar.py`

- **Purpose**: Sidebar controls and filters
- **Key Functions**:
  - `initialize_session_state()`: Initialize session state
  - `render_sidebar()`: Render sidebar with all controls

#### `kpis.py`

- **Purpose**: KPI calculation and display
- **Key Functions**:
  - `calculate_kpis()`: Calculate and display all KPIs

### Feature Modules

#### `live_mode.py`

- **Purpose**: Live mode auto-refresh functionality
- **Key Functions**:
  - `handle_live_mode()`: Handle auto-refresh logic

#### `tabs/overview.py`

- **Purpose**: Overview tab with track telemetry
- **Features**:
  - Lap time trends
  - Speed analysis
  - Fuel consumption
  - Tyre life monitoring
  - Vehicle distribution

#### `tabs/strategy.py`

- **Purpose**: Strategy tab with live pace analysis
- **Features**:
  - Live pace & replay
  - Leaderboard
  - Rolling window analysis
  - Race leader metrics

#### `tabs/pit_wall.py`

- **Purpose**: Pit wall tab with strategy advisor
- **Features**:
  - Pit window analysis
  - Undercut opportunities
  - Vehicle comparison
  - Strategy recommendations

#### `tabs/tyres.py`

- **Purpose**: Tyres tab with tyre health analysis
- **Features**:
  - Tyre life trends
  - Compound comparison
  - Driver performance statistics
  - Best lap distribution

#### `tabs/fuel.py`

- **Purpose**: Fuel tab with fuel strategy
- **Features**:
  - Fuel consumption trends
  - Weather correlation
  - Fuel strategy recommendations

#### `tabs/data.py`

- **Purpose**: Data tab for file upload and inspection
- **Features**:
  - CSV file upload
  - Data inspection
  - Dataset information

## Key Features

### Real-Time Analytics

- **Live Mode**: Auto-updates lap progress every 5-6 seconds
- **Real-Time Telemetry**: Processes live telemetry data
- **Dynamic KPIs**: Updates based on current race state

### Strategic Decision Support

- **Pit Window Analysis**: Optimal pit stop timing
- **Undercut Detection**: Identifies undercut opportunities
- **Strategy Advisor**: AI-powered recommendations

### Comprehensive Analysis

- **Multi-Vehicle Comparison**: Compare performance across vehicles
- **Weather Correlation**: Analyze weather impact on pace
- **Tyre Health Monitoring**: Track tyre degradation
- **Fuel Strategy**: Optimize fuel consumption

## Data Sources

The application uses:

- **Excel Dataset**: `Toyota GR Hackathon Datasets.xlsx`
  - Lap end timestamps
  - Lap time data
  - Weather data
  - Provisional results
- **Telemetry CSVs**:
  - `R1_barber_telemetry_data.csv`
  - `R2_barber_telemetry_data.csv`

## Usage

### Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

   - On macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

   - On Windows:

   ```bash
   venv\Scripts\activate
   ```

3. Install required dependencies:

```bash
pip install streamlit pandas numpy openpyxl pyarrow
```

### Running the Application

```bash
streamlit run main.py
```

### Key Controls

1. **Race Selection**: Choose between Race 1 and Race 2
2. **Vehicle Filter**: Select specific vehicle or view all vehicles
3. **Lap Filter**: Set current lap or enable live mode
4. **Live Mode**: Auto-updates lap progress every 5-6 seconds

### Navigation

- **Overview**: Track telemetry and overall race view
- **Strategy**: Live pace analysis and replay
- **Pit Wall**: Pit window and undercut analysis
- **Tyres**: Tyre health and consistency
- **Fuel**: Fuel strategy and weather correlation
- **Data**: File upload and inspection

## Technical Stack

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Python 3.12+**: Programming language

## Code Quality

- **Modular Design**: Clear separation of concerns
- **Type Hints**: Type annotations for better code clarity
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Robust error handling throughout
- **Performance**: Caching for data loading operations

## Hackathon Category

**Real-Time Analytics**: This application enables race engineers to make split-second strategic decisions during live races by processing real-time telemetry, calculating optimal strategies, and providing AI-powered recommendations.

## Judges' Guide

### Code Organization

- Each module has a single, well-defined responsibility
- Functions are documented with docstrings
- Constants are centralized in `config.py`
- UI components are reusable and modular

### Key Algorithms

- **Lap Time Calculation**: `compute_lap_time_from_timestamps()` in `data_processing.py`
- **Telemetry Processing**: `process_telemetry()` in `telemetry.py`
- **Rolling Consistency**: `rolling_consistency()` in `data_processing.py`
- **KPI Calculations**: `calculate_kpis()` in `kpis.py`

### Data Flow

1. User selects race/vehicle/lap in sidebar
2. Data is loaded and filtered based on selections
3. KPIs are calculated from filtered data
4. Tabs display relevant analysis based on filters
5. Live mode auto-updates when enabled

### Extension Points

- Add new telemetry metrics in `telemetry.py`
- Add new tabs in `tabs/` directory
- Add new KPIs in `kpis.py`
- Modify styling in `ui_components.py`
