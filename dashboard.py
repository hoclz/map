import streamlit as st

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
            font-size: 36px;
            font-weight: bold;
            color: #4A90E2;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 30px;
        }
        .footer {
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #555;
            margin-top: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and subtitle
st.markdown('<p class="title">📊 Illinois Asthma Hospitalization Rates</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Select Year & Race to View the Updated Map</p>', unsafe_allow_html=True)

# Organizing dropdowns in two columns for better layout
col1, col2 = st.columns(2)

with col1:
    year = st.selectbox("📅 Select Year", ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"])
    
with col2:
    race = st.selectbox("🎨 Select Race", ["NHA", "NHB", "NHW", "HISP"])

# API request to Flask for the latest map
map_url = f"http://127.0.0.1:5000/update_map?year={year}&race={race}"

# Display the updated map dynamically
st.image(map_url, caption=f"📌 Asthma Hospitalization for {race} in {year}", use_column_width=True)

# Footer
st.markdown('<div class="footer">Developed by hoclz | Powered by Streamlit 🚀</div>', unsafe_allow_html=True)
