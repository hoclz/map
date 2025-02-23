import streamlit as st
import os
from v9_main_map import plot_illinois_map  # Import the map function

# Set the page config
st.set_page_config(
    page_title="Illinois Asthma Hospitalization Rates",
    layout="wide",
    page_icon="📊",
)

# Apply custom styles
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 35px;
            font-weight: bold;
            color: #4A90E2;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            color: #333333;
        }
        .stSelectbox {
            width: 300px !important;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            text-align: center;
            padding: 10px;
            background-color: #f8f9fa;
            font-size: 14px;
            color: #555;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add Title
st.markdown('<p class="title">📊 Illinois Asthma Hospitalization Rates</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Select Year & Race to View the Map</p>', unsafe_allow_html=True)

# Dropdowns for selecting parameters
col1, col2 = st.columns([1, 1])

with col1:
    selected_year = st.selectbox("📅 Select Year", [2023, 2022, 2021, 2020, 2019])
    
with col2:
    selected_race = st.selectbox("🎨 Select Race", ["NHB", "NHW", "NHA", "HISP"])

# Generate file name for the map
image_path = f"static/maps/{selected_race}_{selected_year}.png"

# Ensure map is generated before displaying
if not os.path.exists(image_path):
    plot_illinois_map(selected_year, selected_race)  # Call your function to generate map

# Display map
if os.path.exists(image_path):
    st.image(image_path, use_column_width=True, caption=f"Asthma Hospitalization for {selected_race} in {selected_year}")
else:
    st.error("🚨 The map could not be generated. Check logs for errors.")

# Add footer
st.markdown('<div class="footer">Developed by hoclz | Powered by Streamlit</div>', unsafe_allow_html=True)



