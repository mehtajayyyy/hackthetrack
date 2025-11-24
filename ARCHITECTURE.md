# RaceIQ Pro - Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit App                         │
│                         (main.py)                            │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Sidebar    │   │     KPIs     │   │  Live Mode   │
│  (sidebar.py)│   │   (kpis.py)   │   │(live_mode.py)│
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│     Data     │   │  Telemetry   │   │      UI       │
│ Processing   │   │ (telemetry.py)│   │ Components   │
│(data_proc.py)│   └──────────────┘   │(ui_comp.py)   │
└──────────────┘                       └──────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Overview   │   │   Strategy   │   │   Pit Wall   │
│   (tabs/)    │   │   (tabs/)    │   │   (tabs/)    │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│    Tyres     │   │     Fuel     │   │     Data     │
│   (tabs/)    │   │   (tabs/)    │   │   (tabs/)    │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Data Flow

### 1. Initialization Flow
```
main.py
  ├─> apply_custom_styles() [ui_components.py]
  ├─> list_sheets() [data_processing.py]
  └─> render_sidebar() [sidebar.py]
      ├─> initialize_session_state()
      └─> build_laps() [data_processing.py]
```

### 2. User Interaction Flow
```
User Action (Sidebar)
  ├─> Race Selection → st.session_state.selected_race
  ├─> Vehicle Selection → st.session_state.selected_vehicle
  └─> Lap Selection → st.session_state.current_lap_filter
      │
      └─> calculate_kpis() [kpis.py]
          ├─> build_laps() [data_processing.py]
          ├─> load_telemetry() [telemetry.py]
          └─> process_telemetry() [telemetry.py]
```

### 3. Tab Rendering Flow
```
Tab Selection
  ├─> render_overview_tab() [tabs/overview.py]
  │   ├─> build_laps() [data_processing.py]
  │   ├─> load_telemetry() [telemetry.py]
  │   └─> process_telemetry() [telemetry.py]
  │
  ├─> render_strategy_tab() [tabs/strategy.py]
  │   └─> build_laps() [data_processing.py]
  │
  ├─> render_pit_wall_tab() [tabs/pit_wall.py]
  │   └─> build_laps() [data_processing.py]
  │
  ├─> render_tyres_tab() [tabs/tyres.py]
  │   ├─> build_laps() [data_processing.py]
  │   └─> load_telemetry() [telemetry.py]
  │
  ├─> render_fuel_tab() [tabs/fuel.py]
  │   ├─> build_laps() [data_processing.py]
  │   └─> load_telemetry() [telemetry.py]
  │
  └─> render_data_tab() [tabs/data.py]
```

### 4. Live Mode Flow
```
Live Mode Toggle ON
  ├─> st.session_state.lap_live = True
  └─> handle_live_mode() [live_mode.py]
      ├─> Check time since last update
      ├─> Increment current_lap_filter
      └─> st.rerun()
          └─> Recalculate all KPIs and tabs
```

## Module Dependencies

```
main.py
  ├─> config.py
  ├─> data_processing.py
  ├─> ui_components.py
  ├─> sidebar.py
  ├─> kpis.py
  ├─> live_mode.py
  └─> tabs/
      ├─> overview.py
      ├─> strategy.py
      ├─> pit_wall.py
      ├─> tyres.py
      ├─> fuel.py
      └─> data.py

sidebar.py
  ├─> config.py
  ├─> data_processing.py
  └─> ui_components.py

kpis.py
  ├─> config.py
  ├─> data_processing.py
  ├─> telemetry.py
  └─> ui_components.py

tabs/*.py
  ├─> config.py
  ├─> data_processing.py
  ├─> telemetry.py (some tabs)
  └─> ui_components.py
```

## Key Design Patterns

### 1. Separation of Concerns
- **Data Layer**: `data_processing.py`, `telemetry.py`
- **Presentation Layer**: `ui_components.py`, `tabs/*.py`
- **Business Logic**: `kpis.py`, `live_mode.py`
- **Configuration**: `config.py`

### 2. Single Responsibility Principle
- Each module has one clear purpose
- Functions are focused and do one thing well
- Easy to test and maintain

### 3. Dependency Injection
- File paths passed as parameters
- Session state managed centrally
- No global state pollution

### 4. Caching Strategy
- `@st.cache_data` on expensive operations
- Data loading cached
- Telemetry processing cached

## Performance Considerations

### Caching
- `build_laps()`: Cached per race
- `load_telemetry()`: Cached per race
- Reduces redundant file I/O

### Data Filtering
- Filter early in the pipeline
- Reduce data size before processing
- Efficient pandas operations

### Live Mode Optimization
- Incremental updates
- Time-based refresh (5.5 seconds)
- Prevents excessive reruns

## Extension Points

### Adding New Metrics
1. Add metric calculation in `telemetry.py`
2. Update `process_telemetry()` function
3. Display in relevant tab

### Adding New Tabs
1. Create new file in `tabs/` directory
2. Implement `render_*_tab(file_source)` function
3. Import and add to `main.py`
4. Update `tabs/__init__.py`

### Adding New KPIs
1. Add calculation in `kpis.py`
2. Update `calculate_kpis()` function
3. Add KPI card display

### Modifying UI
1. Update styles in `ui_components.py`
2. Modify components as needed
3. Update tab layouts in `tabs/*.py`

## Testing Strategy

### Unit Testing (Recommended)
- Test data processing functions
- Test telemetry processing
- Test KPI calculations

### Integration Testing (Recommended)
- Test tab rendering
- Test sidebar interactions
- Test live mode functionality

### Manual Testing
- Run `streamlit run main.py`
- Test all filters and controls
- Verify data accuracy

## Code Quality Metrics

- **Modularity**: High (clear separation)
- **Maintainability**: High (well-documented)
- **Extensibility**: High (clear extension points)
- **Readability**: High (clear naming, docstrings)
- **Performance**: Good (caching, efficient operations)

