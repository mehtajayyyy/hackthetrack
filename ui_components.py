"""
UI Components Module
=====================
Contains reusable UI components, styling, and helper functions.
"""

import streamlit as st
from typing import Optional

from config import PRIMARY, ACCENT, WARNING, DANGER, MUTED, BRAND_NAME, BRAND_TAGLINE


def apply_custom_styles():
    """
    Apply custom CSS styles to the Streamlit app.
    """
    st.markdown(
        f"""
        <style>
            :root {{
                --primary: {PRIMARY};
                --accent: {ACCENT};
                --warning: {WARNING};
                --danger:  {DANGER};
                --muted:   {MUTED};
            }}

            /* App chrome */
            .block-container {{
                padding-top: 0.5rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }}
            
            /* Main content area improvements */
            .main .block-container {{
                padding-left: 2rem;
                padding-right: 2rem;
            }}
            
            /* Better spacing for first view */
            [data-testid="stVerticalBlock"] {{
                gap: 1rem;
            }}
            
            /* KPI cards spacing */
            .element-container:has(.kpi) {{
                margin-bottom: 1.5rem;
            }}
            
            /* Remove toolbar */
            [data-testid="stAppToolbar"] {{
                display: none !important;
            }}
            [data-testid="stToolbar"] {{
                display: none !important;
            }}
            
            .stAppHeader {{
                display: none !important;
            }}
            [data-testid="stSidebarHeader"] {{
                display: none !important;
            }}
            
            header[data-testid="stHeader"] {{
                background: linear-gradient(135deg, rgba(15,98,254,0.10), rgba(36,161,72,0.08));
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }}
            
            /* Enhanced Sidebar */
            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
                border-right: 2px solid rgba(15,98,254,0.15);
                box-shadow: 2px 0 8px rgba(0,0,0,0.05);
            }}
            
            [data-testid="stSidebar"] .css-1d391kg {{
                padding-top: 1.5rem;
            }}
            
            [data-testid="stSidebar"] h3 {{
                color: {PRIMARY} !important;
                font-weight: 700 !important;
                font-size: 1.1rem !important;
                margin-bottom: 1rem !important;
                padding-bottom: 0.5rem !important;
                border-bottom: 2px solid {PRIMARY} !important;
            }}
            
            [data-testid="stSidebar"] .stRadio {{
                background: white;
                padding: 0.75rem;
                border-radius: 8px;
                border: 1px solid rgba(15,98,254,0.1);
                margin-bottom: 0.5rem;
            }}
            
            [data-testid="stSidebar"] .stSelectbox {{
                background: white;
                border-radius: 6px;
            }}
            
            [data-testid="stSidebar"] .stSlider {{
                padding: 0.5rem 0;
            }}
            
            [data-testid="stSidebar"] .stMetric {{
                background: white;
                padding: 0.75rem;
                border-radius: 8px;
                border: 1px solid rgba(15,98,254,0.1);
                margin-bottom: 0.5rem;
            }}
            
            [data-testid="stSidebar"] hr {{
                border-color: rgba(15,98,254,0.2);
                margin: 1rem 0;
            }}
            
            [data-testid="stSidebar"] .stCaption {{
                color: {MUTED};
                font-size: 0.8rem;
                font-style: italic;
            }}

            /* Headings */
            h1, h2, h3, h4 {{ letter-spacing: .2px; }}
            h1 {{ font-size: 1.8rem; margin-bottom: .25rem; }}
            .subtitle {{ color: #68707A; margin-bottom: .75rem; }}

            /* KPI cards */
            .kpi {{
                border: 1px solid rgba(0,0,0,0.07);
                border-radius: 16px;
                padding: 16px 18px;
                background: white;
                box-shadow: 0 2px 18px rgba(0,0,0,0.03);
                height: 100%;
            }}
            .kpi .label {{ font-size: .85rem; color: #67707A; margin-bottom: 6px; }}
            .kpi .value {{ font-weight: 700; font-size: 1.4rem; }}
            .kpi .delta {{ font-size: .8rem; opacity: 0.9; }}

            /* Enhanced Tabs - Bigger and more visible */
            .stTabs {{
                margin-top: 1.5rem;
                margin-bottom: 1rem;
            }}
            
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background: #f8f9fa;
                padding: 8px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            
            .stTabs [data-baseweb="tab"] {{
                padding: 16px 28px !important;
                border-radius: 8px !important;
                font-size: 1.05rem !important;
                font-weight: 600 !important;
                min-height: 56px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                transition: all 0.3s ease !important;
                background: white !important;
                color: {MUTED} !important;
                border: 2px solid transparent !important;
            }}
            
            .stTabs [data-baseweb="tab"]:hover {{
                background: rgba(15,98,254,0.05) !important;
                color: {PRIMARY} !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(15,98,254,0.15);
            }}
            
            .stTabs [aria-selected="true"] {{
                background: linear-gradient(135deg, {PRIMARY} 0%, #3b82f6 100%) !important;
                color: white !important;
                border-bottom: 3px solid {PRIMARY} !important;
                box-shadow: 0 4px 12px rgba(15,98,254,0.3) !important;
                transform: translateY(-2px);
            }}
            
            .stTabs [aria-selected="true"]:hover {{
                background: linear-gradient(135deg, {PRIMARY} 0%, #3b82f6 100%) !important;
                color: white !important;
            }}

            /* Badges */
            .badge {{
                display:inline-flex;
                gap:8px;
                align-items:center;
                padding:3px 10px;
                border-radius:999px;
                font-size:.8rem;
                border:1px solid rgba(0,0,0,0.08);
            }}
            .b-ok    {{ background:#ECF3FF; color:#0F62FE; }}
            .b-warn  {{ background:#FFF2E9; color:#FF832B; }}
            .b-crit  {{ background:#FFEAF0; color:#DA1E28; }}

            /* Data cards */
            .card {{
                border: 1px solid rgba(0,0,0,0.07);
                border-radius: 16px;
                padding: 18px;
                background: white;
                box-shadow: 0 2px 18px rgba(0,0,0,0.03);
            }}
            .card h3 {{ margin: 0 0 .5rem 0; font-size: 1.05rem; }}
            
            /* Dataframe styling */
            div[data-testid="stDataFrame"] {{
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            div[data-testid="stDataFrame"] thead {{
                background: linear-gradient(135deg, {PRIMARY} 0%, #3b82f6 100%);
            }}
            div[data-testid="stDataFrame"] thead th {{
                color: white !important;
                font-weight: 600;
            }}
            
            /* Remove toolbar from main canvas */
            .stApp > header {{
                visibility: hidden;
                height: 0;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_branding():
    """Render the branding header in the sidebar."""
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid {PRIMARY};">
            <h1 style="font-size: 2rem; font-weight: 800; color: {PRIMARY}; letter-spacing: -0.02em; padding-bottom: 0rem;">
                {BRAND_NAME}
            </h1>
            <p style="font-size: 1.3rem; color: {MUTED}; margin: 0; font-weight: 500;">
                {BRAND_TAGLINE}
            </p>
        </div>
    """, unsafe_allow_html=True)


def kpi(label: str, value: str, delta: Optional[str] = None, klass: str = "b-ok"):
    """
    Render a KPI card component.
    
    Args:
        label: KPI label text
        value: KPI value to display
        delta: Optional delta/badge text
        klass: CSS class for badge ("b-ok", "b-warn", "b-crit")
    """
    delta_html = f'<span class="badge {klass}">{delta}</span>' if delta else ""
    st.markdown(
        f'<div class="kpi">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="delta">{delta_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def section(title: str, help_text: Optional[str] = None):
    """
    Render a section header with optional help text.
    
    Args:
        title: Section title
        help_text: Optional help/description text
    """
    col_title, col_help = st.columns([1, 4])
    with col_title:
        st.subheader(title)
    with col_help:
        if help_text:
            st.caption(help_text)


def render_vehicle_banner(vehicle_id: str, race: str, current_lap: int, total_laps: int):
    """
    Render a banner showing current analysis context.
    
    Args:
        vehicle_id: Selected vehicle ID
        race: Selected race name
        current_lap: Current lap number
        total_laps: Total laps in race
    """
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ECF3FF 0%, #f0f4f8 100%); 
                    padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border-left: 4px solid {PRIMARY};">
            <p style="margin: 0; font-weight: 600; color: {PRIMARY}; font-size: 1.1rem;">
                📊 Analyzing: <strong>{vehicle_id}</strong> | Race: {race} | Lap: {current_lap}/{total_laps}
            </p>
        </div>
    """, unsafe_allow_html=True)

