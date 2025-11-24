"""
Tabs Module
===========
Contains all tab components for the RaceIQ Pro dashboard.
"""

from .overview import render_overview_tab
from .strategy import render_strategy_tab
from .pit_wall import render_pit_wall_tab
from .tyres import render_tyres_tab
from .fuel import render_fuel_tab
from .data import render_data_tab

__all__ = [
    'render_overview_tab',
    'render_strategy_tab',
    'render_pit_wall_tab',
    'render_tyres_tab',
    'render_fuel_tab',
    'render_data_tab',
]

