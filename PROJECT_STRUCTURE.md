# RaceIQ Pro - Project Structure Summary

## Quick Start for Judges

### To Run the Application

```bash
streamlit run main.py
```

### File Organization

```
RaceIQ Pro/
│
├── main.py                          # 🚀 START HERE - Main entry point
│
├── Core Configuration
│   └── config.py                    # All constants, sheet names, colors
│
├── Data Layer
│   ├── data_processing.py           # Excel operations, lap calculations
│   └── telemetry.py                 # Telemetry CSV processing
│
├── UI Layer
│   ├── ui_components.py             # Styling, KPI cards, UI helpers
│   ├── sidebar.py                   # Sidebar controls & filters
│   └── kpis.py                      # KPI calculations & display
│
├── Features
│   └── live_mode.py                 # Auto-refresh logic
│
└── Tabs (Feature Modules)
    └── tabs/
        ├── __init__.py              # Tab exports
        ├── overview.py              # Track telemetry overview
        ├── strategy.py              # Live pace & replay
        ├── pit_wall.py              # Pit window analysis
        ├── tyres.py                 # Tyre health analysis
        ├── fuel.py                  # Fuel strategy
        └── data.py                  # Data upload/inspection
```

## Code Quality Highlights

### ✅ Modular Design

- **Single Responsibility**: Each module has one clear purpose
- **Separation of Concerns**: Data, UI, and logic are separated
- **Easy to Navigate**: Clear file structure

### ✅ Documentation

- **Docstrings**: All functions documented
- **Type Hints**: Type annotations throughout
- **README**: Comprehensive documentation

### ✅ Best Practices

- **Constants Centralized**: All in `config.py`
- **Error Handling**: Robust error handling
- **Caching**: Performance optimization with `@st.cache_data`
- **Session State**: Proper state management

### ✅ Maintainability

- **Clear Naming**: Descriptive function and variable names
- **Consistent Style**: PEP 8 compliant
- **Extension Points**: Easy to add new features

## Key Algorithms

### 1. Lap Time Calculation

**Location**: `data_processing.py::compute_lap_time_from_timestamps()`

- Calculates lap times from timestamp differences
- Handles per-vehicle calculations
- Robust error handling

### 2. Telemetry Processing

**Location**: `telemetry.py::process_telemetry()`

- Extracts speed, fuel, tyre, acceleration metrics
- Pivots data for analysis
- Filters by vehicle and lap range

### 3. KPI Calculations

**Location**: `kpis.py::calculate_kpis()`

- Gap to leader calculation
- Fuel estimation from throttle usage
- Tyre life estimation from brake usage

### 4. Rolling Consistency

**Location**: `data_processing.py::rolling_consistency()`

- Median Absolute Deviation (MAD) based
- Robust to outliers
- Rolling window calculation

## Data Flow Summary

```
User Input (Sidebar)
    ↓
Session State Update
    ↓
Data Loading (Cached)
    ↓
Data Filtering
    ↓
KPI Calculation
    ↓
Tab Rendering
    ↓
Display
```

## Extension Guide

### To Add a New Tab

1. Create `tabs/new_tab.py`
2. Implement `render_new_tab(file_source)` function
3. Import in `tabs/__init__.py`
4. Add to `main.py` tabs list

### To Add a New KPI

1. Add calculation in `kpis.py::calculate_kpis()`
2. Add KPI card using `kpi()` function
3. Update display in main content area

### To Add a New Telemetry Metric

1. Add extraction logic in `telemetry.py::process_telemetry()`
2. Use in relevant tabs
3. Update KPI calculations if needed

## Testing Checklist

- [ ] All tabs render correctly
- [ ] Filters update data properly
- [ ] Live mode auto-updates
- [ ] KPIs calculate correctly
- [ ] Telemetry data processes correctly
- [ ] Error handling works
- [ ] UI is responsive

## Performance Notes

- **Caching**: Data loading operations are cached
- **Efficient Filtering**: Early filtering reduces processing
- **Optimized Pandas**: Vectorized operations where possible
- **Live Mode**: Time-based refresh prevents excessive reruns

## Hackathon Category

**Real-Time Analytics** - This application enables real-time decision-making for race engineers with:

- Live telemetry processing
- Real-time KPI updates
- Auto-refreshing live mode
- Strategic recommendations
- Pit window optimization
