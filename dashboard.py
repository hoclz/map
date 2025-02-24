import streamlit as st
from v9_main_map import plot_illinois_map

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
        .stPlot {
            border-radius: 15px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
    # Convert to integer for the map function
    year = st.selectbox(
        "📅 Select Year",
        options=[2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        key="selected_year"
    )
    
with col2:
    race = st.selectbox(
        "🎨 Select Race",
        options=["NHB", "NHW", "NHA", "HISP"],
        format_func=lambda x: {
            "NHB": "Non-Hispanic Black",
            "NHW": "Non-Hispanic White",
            "NHA": "Non-Hispanic Asian",
            "HISP": "Hispanic"
        }[x],
        key="selected_race"
    )

# Display the map visualization
try:
    plot_illinois_map()
except Exception as e:
    st.error(f"Error generating map: {str(e)}")

# Footer
st.markdown(
    '<div class="footer">Developed by hoclz | Powered by Streamlit 🚀</div>',
    unsafe_allow_html=True
)
