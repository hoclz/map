import streamlit as st
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import unary_union

# Ensure the correct working directory
STATIC_MAP_FOLDER = "static/maps"
os.makedirs(STATIC_MAP_FOLDER, exist_ok=True)

# Define available years and races
YEARS = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
RACES = {
    "NHA": "Non-Hispanic Asian",
    "NHB": "Non-Hispanic Black",
    "NHW": "Non-Hispanic White",
    "HISP": "Hispanic",
}

# Streamlit Page Config
st.set_page_config(
    page_title="Illinois Asthma Hospitalization",
    layout="centered",
    page_icon="📊"
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #007BFF;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #666;
            margin-top: 30px;
        }
        .stAlert {
            background-color: #fff9db !important;
            border-radius: 10px;
        }
        .stSelectbox label {
            font-size: 14px !important;
            font-weight: bold !important;
            color: #5a5a5a !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and subtitle
st.markdown('<p class="title">📊 Illinois Asthma Hospitalization Rates</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Select Year & Race to View the Updated Map</p>', unsafe_allow_html=True)

# Organizing dropdowns in two columns for better layout
col1, col2 = st.columns([1, 1])

with col1:
    PARAM_YEAR = st.selectbox("📅 Select Year", YEARS, index=len(YEARS) - 1)
    
with col2:
    PARAM_RACE = st.selectbox("🎨 Select Race", list(RACES.keys()), format_func=lambda x: RACES[x])

# Define paths
map_filename = os.path.join(STATIC_MAP_FOLDER, f"{PARAM_RACE}_{PARAM_YEAR}.png")

# Check if map exists, otherwise warn user
if os.path.exists(map_filename):
    st.image(map_filename, caption=f"📌 Asthma Hospitalization for {RACES[PARAM_RACE]} in {PARAM_YEAR}", use_column_width=True)
else:
    st.warning(f"⚠️ No map found for {RACES[PARAM_RACE]} in {PARAM_YEAR}. Please generate the map first.")

# Footer
st.markdown('<div class="footer">Developed by hoclz | Powered by Streamlit 🚀</div>', unsafe_allow_html=True)
