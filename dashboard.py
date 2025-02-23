import streamlit as st
import os

# Set up the page configuration
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

# Organize dropdowns in two columns
col1, col2 = st.columns([1, 1])

with col1:
    year = st.selectbox("📅 Select Year", ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"])
with col2:
    race = st.selectbox("🎨 Select Race", ["NHA", "NHB", "NHW", "HISP"])

# Path to the generated map file in static/maps/
map_filename = f"static/maps/{race}_{year}.png"

# Display the map if found, otherwise show a warning
if os.path.exists(map_filename):
    st.image(map_filename, caption=f"📌 Asthma Hospitalization for {race} in {year}", use_column_width=True)
else:
    st.warning("⚠️ Map file not found. Make sure v9_main_map.py has generated the image in 'static/maps/'.")

# Footer
st.markdown('<div class="footer">Developed by hoclz | Powered by Streamlit 🚀</div>', unsafe_allow_html=True)


