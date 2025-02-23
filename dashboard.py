import streamlit as st

st.title("Illinois Asthma Hospitalization Rates")

# Dropdowns for selection
year = st.selectbox("Select Year", ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"])
race = st.selectbox("Select Race", ["NHA", "NHB", "NHW", "HISP"])

# API request to Flask for the latest map
map_url = f"http://127.0.0.1:5000/update_map?year={year}&race={race}"

# Display the updated map dynamically
st.image(map_url, caption=f"Asthma Hospitalization for {race} in {year}")
