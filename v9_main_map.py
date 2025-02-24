import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.patheffects import withStroke
from matplotlib.table import Table
from shapely.ops import unary_union
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import os

# -------------------------------------------------------------------------
# 1) PARAMETERS (Updated for Streamlit)
# -------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Illinois Asthma Dashboard")

st.title("Illinois Asthma Dashboard")
st.sidebar.header("Select Parameters")

# Dropdown for selecting year
PARAM_YEAR = st.sidebar.selectbox("Select Year", options=[2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016])

# Dropdown for selecting race
race_options = {"NHB": "Non-Hispanic Black", "NHW": "Non-Hispanic White", 
                "NHA": "Non-Hispanic Asian", "HISP": "Hispanic"}
PARAM_RACE = st.sidebar.selectbox("Select Race/Ethnicity", list(race_options.keys()), format_func=lambda x: race_options[x])

# File paths based on GitHub repository structure
CSV_PATH = "Asthma_regional_data.csv"
COUNTY_TYPE_CSV = "county_type.csv"
TOTAL_COUNT_CSV = "total_count_per_race_ethnicity.csv"
ILLINOIS_GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/illinois-counties.geojson"

# Path to static folder for saving generated maps
STATIC_MAP_FOLDER = "static/maps"
LOGO_PATH = "static/maps/IDPH_logo.png"

# Define a dictionary of high-contrast colors for dynamic line color
dynamic_line_color = {"NHB": "#E41A1C", "NHW": "#377EB8", "NHA": "#4DAF4A", "HISP": "#984EA3"}
LINE_COLOR = dynamic_line_color[PARAM_RACE.upper()]


# ------------------------------------------------------------------------- 
# 2) READ & PREPARE THE ASTHMA DATA (Optimized for Streamlit)
# -------------------------------------------------------------------------

@st.cache_data
def load_asthma_data():
    """Loads and preprocesses asthma regional data."""
    df = pd.read_csv(CSV_PATH)

    rename_map = {
        "Group": "Race",
        "_2016": "2016", "_2017": "2017", "_2018": "2018", "_2019": "2019",
        "_2020": "2020", "_2021": "2021", "_2022": "2022", "_2023": "2023"
    }
    df = df.rename(columns=rename_map)

    # Reshape data for analysis
    year_cols = [str(year) for year in range(2016, 2024)]
    df_melted = df.melt(id_vars=["Race", "Region"], value_vars=year_cols, 
                         var_name="Year", value_name="Rate")
    df_melted["Year"] = df_melted["Year"].astype(int)

    return df_melted

df_melted = load_asthma_data()

# Filter data based on Streamlit inputs
df_filtered = df_melted[
    (df_melted["Year"] == PARAM_YEAR) & 
    (df_melted["Race"].str.upper() == PARAM_RACE.upper())
]

if df_filtered.empty:
    st.warning(f"⚠️ No data found for {PARAM_RACE} in {PARAM_YEAR}. Check your dataset or parameters.")
    st.stop()

# Build table_data: first row = Race acronym, then "Region, Rate" rows
table_data = [[PARAM_RACE.upper()]] + [
    [f"{row['Region']}, {row['Rate']}"] for _, row in df_filtered.iterrows()
]

# 2.5) Sort table rows by rate (descending order)
header = table_data[0]
data_rows = table_data[1:]

parsed = []
for row_item in data_rows:
    region, val_str = row_item[0].split(",", 1)
    parsed.append((region.strip(), float(val_str.strip())))

parsed.sort(key=lambda x: x[1], reverse=True)
table_data = [header] + [[f"{r}, {v}"] for (r, v) in parsed]

# ------------------------------------------------------------------------- 
# 3) BUILD THE CIRCLE VALUES FROM "statewide" ROWS (for each race)
# -------------------------------------------------------------------------

@st.cache_data
def get_statewide_circle_values(df_melted, year):
    """
    Extracts the statewide asthma rate per 100,000 population 
    for each race in the selected year.
    """
    valid_circle_races = ["NHB", "NHW", "NHA", "HISP"]

    df_circle = df_melted[(df_melted["Year"] == year) & 
                          (df_melted["Region"].str.lower() == "statewide")]

    circle_dict = {}
    for rc in valid_circle_races:
        row_rc = df_circle[df_circle["Race"].str.upper() == rc]
        if row_rc.empty:
            st.warning(f"⚠️ No 'statewide' row found for {rc} in {year}.")
            circle_dict[rc] = "N/A"
        else:
            circle_dict[rc] = str(row_rc["Rate"].iloc[0])

    return circle_dict

# Get statewide rates for selected year
circle_dict = get_statewide_circle_values(df_melted, PARAM_YEAR)

# Keep track of the selected year
selected_year = PARAM_YEAR

# ------------------------------------------------------------------------- 
# 4) READ & PREPARE THE ILLINOIS COUNTY GEOMETRY (Optimized for Streamlit)
# -------------------------------------------------------------------------

@st.cache_data
def load_county_geometry():
    """
    Loads the Illinois county geometries, merges them with county types, 
    assigns regions, and prepares for visualization.
    """
    try:
        # Load county geometries
        illinois = gpd.read_file(ILLINOIS_GEOJSON_URL).to_crs(epsg=26971)
        state_boundary = illinois.dissolve()

        # Load county type data
        df_county_type = pd.read_csv(COUNTY_TYPE_CSV)

        # Merge county data with type data
        illinois = illinois.merge(df_county_type, left_on="name", right_on="County", how="left")

        # Define Illinois regions
        regions = {
            "NORTH": [
                "Boone", "Carroll", "Dekalb", "Jo Daviess", "Lee", "Ogle",
                "Stephenson", "Whiteside", "Winnebago"
            ],
            "NORTH-CENTRAL": [
                "Bureau", "Fulton", "Grundy", "Henderson", "Henry", "Kendall", "Knox",
                "Lasalle", "Livingston", "Marshall", "Mcdonough", "Mclean", "Mercer",
                "Peoria", "Putnam", "Rock Island", "Stark", "Tazewell", "Warren", "Woodford"
            ],
            "WEST-CENTRAL": [
                "Adams", "Brown", "Calhoun", "Cass", "Christian", "Greene", "Hancock",
                "Jersey", "Logan", "Macoupin", "Mason", "Menard", "Montgomery",
                "Morgan", "Pike", "Sangamon", "Schuyler", "Scott"
            ],
            "METRO EAST": [
                "Bond", "Clinton", "Madison", "Monroe", "Randolph", "St. Clair", "Washington"
            ],
            "SOUTHERN": [
                "Alexander", "Edwards", "Franklin", "Gallatin", "Hamilton", "Hardin", "Jackson",
                "Jefferson", "Johnson", "Marion", "Massac", "Perry", "Pope", "Pulaski",
                "Saline", "Union", "Wabash", "Wayne", "White", "Williamson"
            ],
            "EAST-CENTRAL": [
                "Champaign", "Clark", "Clay", "Coles", "Crawford", "Cumberland", "Dewitt",
                "Douglas", "Edgar", "Effingham", "Fayette", "Ford", "Iroquois", "Jasper",
                "Lawrence", "Macon", "Moultrie", "Piatt", "Richland", "Shelby", "Vermilion"
            ],
            "SOUTH SUBURBAN": ["Kankakee", "Will"],
            "WEST SUBURBAN": ["Dupage", "Kane"],
            "NORTH SUBURBAN": ["Lake", "Mchenry"],
            "COOK": ["Cook"],
        }

        # Assign regions
        illinois["Region"] = "Other"
        for region_name, county_list in regions.items():
            illinois.loc[illinois["name"].isin(county_list), "Region"] = region_name

        # Define region colors
        region_colors = {
            "NORTH": (102/255, 205/255, 170/255),
            "NORTH-CENTRAL": (255/255, 206/255, 250/255),
            "WEST-CENTRAL": (245/255, 245/255, 220/255),
            "METRO EAST": (255/255, 160/255, 122/255),
            "SOUTHERN": (195/255, 243/255, 253/255),
            "EAST-CENTRAL": (255/255, 215/255, 0/255),
            "SOUTH SUBURBAN": (102/255, 255/255, 102/255),
            "WEST SUBURBAN": (255/255, 0/255, 0/255),
            "NORTH SUBURBAN": (211/255, 211/255, 211/255),
            "COOK": (255/255, 255/255, 255/255),
        }
        illinois["color"] = illinois["Region"].map(region_colors)

        # Define region labels
        region_labels = {
            "NORTH": (250000, 4600000, 1),
            "NORTH-CENTRAL": (350000, 4400000, 2),
            "WEST-CENTRAL": (200000, 4200000, 3),
            "METRO EAST": (700000, 4100000, 4),
            "SOUTHERN": (500000, 3900000, 5),
            "EAST-CENTRAL": (500000, 4400000, 6),
            "SOUTH SUBURBAN": (800000, 4500000, 7),
            "WEST SUBURBAN": (900000, 4600000, 8),
            "NORTH SUBURBAN": (950000, 4700000, 9),
            "COOK": (1050000, 4600000, 10),
        }

        return illinois, state_boundary, region_colors, region_labels

    except Exception as e:
        st.warning(f"⚠️ Error loading county data: {e}")
        return None, None, None, None

# Load county geometry data
illinois, state_boundary, region_colors, region_labels = load_county_geometry()

# Define sources text
sources_text = f"""**Sources**
- Population: Census Data, {PARAM_YEAR}
- Asthma Count: Hospital Discharge Data, {PARAM_YEAR}
- Urban/Rural: Illinois Department of Public Health (IDPH)
- Region: [Chicago Tribune - Illinois Tier Mitigations](https://graphics.chicagotribune.com/illinois-tier-mitigations/map-blurb.html)
"""

# ------------------------------------------------------------------------- 
# 5) HELPER FUNCTIONS (Optimized for Streamlit)
# -------------------------------------------------------------------------

def add_image(ax, image_path, position, zoom):
    """
    Adds an image to the plot at the specified position.
    """
    try:
        img = plt.imread(image_path)
        imagebox = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(imagebox, position, frameon=False, xycoords='axes fraction')
        ax.add_artist(ab)
    except FileNotFoundError:
        st.warning(f"⚠️ Image file not found: {image_path}")

def add_illinois_outline(fig, ax, boundary_gdf, position, zoom):
    """
    Adds an Illinois state outline inset map.
    """
    inset_ax = fig.add_axes([position[0], position[1], zoom, zoom])
    boundary_gdf.boundary.plot(ax=inset_ax, linewidth=2, edgecolor=LINE_COLOR)
    inset_ax.axis('off')

def draw_circle_with_cord(ax, center_x, center_y, radius, value, cord_x, cord_y, label="", highlight=False):
    """
    Draws a labeled circle with a connecting cord.
    """
    angle = np.arctan2(cord_y - center_y, cord_x - center_x)
    contact_x = center_x + radius * np.cos(angle)
    contact_y = center_y + radius * np.sin(angle)

    circle = patches.Circle((center_x, center_y), radius, color=LINE_COLOR, fill=False, linewidth=1.5)
    ax.add_patch(circle)

    ax.text(center_x, center_y, value, ha="center", va="center", fontsize=9)
    
    label_fontweight = "bold" if highlight else "normal"
    ax.text(cord_x, cord_y + 0.15 if highlight else cord_y + 0.1, label.upper(),
            ha="center", va="center", fontsize=9, fontweight=label_fontweight)
    
    ax.plot([cord_x, contact_x], [cord_y, contact_y], color=LINE_COLOR, linewidth=1)

def draw_complete_diagram(fig, ax, position, circle_dict):
    """
    Draws a complete asthma rate diagram based on the `circle_dict` values.
    """
    diagram_ax = fig.add_axes(position)
    diagram_ax.axis("off")

    edge_length_factor = 0.8
    base_length = 1.8
    length = base_length * edge_length_factor
    angle = 60
    y_offset = 1.5
    vertical_line_length = 1.6
    circle_radius = 0.14
    fan_count = 8
    fan_angle = 120
    scale_factor = 0.78

    x_left = -length * np.cos(np.radians(angle / 2))
    y_left = length * np.sin(np.radians(angle / 2)) + y_offset
    x_right = length * np.cos(np.radians(angle / 2))
    y_right = length * np.sin(np.radians(angle / 2)) + y_offset
    apex_x, apex_y = 0, y_offset
    vertical_x, vertical_y = apex_x, apex_y - vertical_line_length

    # Draw the funnel lines using the dynamic line color
    diagram_ax.plot([x_left, apex_x], [y_left, apex_y], color=LINE_COLOR, linewidth=2)
    diagram_ax.plot([apex_x, x_right], [apex_y, y_right], color=LINE_COLOR, linewidth=2)
    diagram_ax.plot([vertical_x, vertical_x], [apex_y, vertical_y], color=LINE_COLOR, linewidth=2)

    # Small "fan" lines at the bottom
    for i in range(fan_count):
        angle_offset = -fan_angle / 2 + i * (fan_angle / (fan_count - 1))
        x_fan = vertical_x + 0.3 * np.sin(np.radians(angle_offset))
        y_fan = vertical_y - 0.3 * np.cos(np.radians(angle_offset))
        diagram_ax.plot([vertical_x, x_fan], [vertical_y, y_fan], color=LINE_COLOR, linewidth=1)

    # Extract statewide values
    val_nhb = circle_dict.get("NHB", "N/A")
    val_nhw = circle_dict.get("NHW", "N/A")
    val_nha = circle_dict.get("NHA", "N/A")
    val_hisp = circle_dict.get("HISP", "N/A")

    # Draw labeled circles
    draw_circle_with_cord(diagram_ax, (x_left + apex_x) / 2, (y_left + apex_y) / 2 - 0.3,
                          circle_radius, val_nhb, (x_left + apex_x) / 2, (y_left + apex_y + 0.03) / 2,
                          label="NHB", highlight=(PARAM_RACE.upper() == "NHB"))
    
    draw_circle_with_cord(diagram_ax, (x_left + apex_x * 2) / 3, (y_left + apex_y * 2) / 3 - 0.4,
                          circle_radius, val_nhw, (x_left + apex_x * 2) / 3, (y_left + apex_y * 2) / 3,
                          label="NHW", highlight=(PARAM_RACE.upper() == "NHW"))
    
    draw_circle_with_cord(diagram_ax, (x_right + apex_x) / 2, (y_right + apex_y) / 2 - 0.3,
                          circle_radius, val_nha, (x_right + apex_x) / 2, (y_right + apex_y) / 2,
                          label="NHA", highlight=(PARAM_RACE.upper() == "NHA"))
    
    draw_circle_with_cord(diagram_ax, (x_right + apex_x * 2) / 3, (y_right + apex_y * 2) / 3 - 0.4,
                          circle_radius, val_hisp, (x_right + apex_x * 2) / 3, (y_right + apex_y * 2) / 3,
                          label="HISP", highlight=(PARAM_RACE.upper() == "HISP"))

    # Legend items
    legend_items = {
        "NHA": "Non-Hispanic Asian",
        "NHB": "Non-Hispanic Black",
        "NHW": "Non-Hispanic White",
        "HISP": "Hispanic"
    }
    
    y_legend_start = vertical_y + 0.6
    line_spacing = 0.3
    for i, (rc, desc) in enumerate(legend_items.items()):
        txt_line = f"{rc} = {desc}"
        fontweight = "bold" if rc == PARAM_RACE.upper() else "normal"
        diagram_ax.text(apex_x + 1, y_legend_start - i * line_spacing, txt_line,
                        fontsize=9, ha="center", fontweight=fontweight, color="black")

    diagram_ax.set_xlim(-length * scale_factor, length * scale_factor)
    diagram_ax.set_ylim(-length * scale_factor, (y_offset + length) * scale_factor)
    diagram_ax.set_aspect('equal', adjustable='box')

    plt.title(f"Statewide Asthma Age-Adjusted Rate Per 100,000 by Race/Ethnicity ({selected_year})",
              fontsize=9, y=1.05)

# -------------------------------------------------------------------------
# 6) ADD ELEMENTS TO THE MAP (Optimized for Streamlit)
# -------------------------------------------------------------------------

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(14, 8))

# Ensure the static folder exists
if not os.path.exists(STATIC_MAP_FOLDER):
    os.makedirs(STATIC_MAP_FOLDER)

# Ensure total count exists before displaying it
if "TOTAL_COUNT" not in globals():
    st.warning("⚠️ Total count is missing. Check your dataset.")
    TOTAL_COUNT = "N/A"  # Default to "N/A" if not available

# IDPH LOGO (#6) - Adjusted for Streamlit Deployment
LOGO_PATH = "static/maps/IDPH_logo.png"
if os.path.exists(LOGO_PATH):
    add_image(ax, LOGO_PATH, (0.35, 0.07), zoom=0.25)
else:
    st.warning("⚠️ IDPH logo file not found. Make sure it's in `static/maps/`.")

# SMALL ILLINOIS OUTLINE (#9)
if state_boundary is not None:
    add_illinois_outline(fig, ax, state_boundary, position=(0.63, 0.65), zoom=0.057)
else:
    st.warning("⚠️ Illinois boundary data missing. Check the geoJSON file.")

# T=TOTAL_COUNT (#10) - Dynamic Text Display
ax.text(
    0.70, 0.74,
    f"T={TOTAL_COUNT}",
    transform=ax.transAxes,
    fontsize=9,
    color='black',
    ha='left',
    va='center'
)

# COMPLETE DIAGRAM (#11)
if circle_dict:
    draw_complete_diagram(fig, ax, [0.64, 0.03, 0.15, 0.5], circle_dict)
else:
    st.warning("⚠️ Circle values are missing. Diagram may not display correctly.")

# FINAL TITLE (#2) using Dynamic Formatting
race_descriptions = {
    "NHB": "Non-Hispanic Black",
    "NHW": "Non-Hispanic White",
    "NHA": "Non-Hispanic Asian",
    "HISP": "Hispanic",
}
full_text = race_descriptions.get(PARAM_RACE.upper(), "Unknown Race")

# Define title components
title_part1 = "Regional Asthma Age-Adjusted Rates Per 100,000 HOSPITALIZATION Discharges for"
title_part2 = f"{full_text} ({PARAM_RACE.upper()})"
title_part3 = f"Population, {selected_year}"

# Define dynamic color for title
title_color = "black"

# Apply the title
ax.set_title(f"{title_part1} {title_part2} {title_part3}", 
             fontsize=12, color=title_color, fontweight="normal", x=0.54, y=1.05)

# Final Adjustments
ax.set_aspect('equal', adjustable='datalim')
ax.set_axis_off()

# Define output path
OUTPUT_FOLDER = "static/maps"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Define file path for saved figure
map_filename = f"{OUTPUT_FOLDER}/{PARAM_RACE}_{PARAM_YEAR}.png"

# Ensure the map is generated before displaying
map_filename = plot_illinois_map(fig_width=14, fig_height=8)

# Display the saved image in Streamlit
if map_filename and os.path.exists(map_filename):
    st.subheader(f"Generated Map for {race_descriptions.get(PARAM_RACE.upper(), PARAM_RACE)} ({PARAM_YEAR})")
    st.image(map_filename, caption=f"Asthma Rates for {PARAM_RACE.upper()}, {PARAM_YEAR}", use_column_width=True)
else:
    st.warning("⚠️ Map could not be generated. Check dataset and parameters.")


# -------------------------------------------------------------------------
# 7) RUN THE PLOT (Optimized for Streamlit Deployment)
# -------------------------------------------------------------------------

def plot_illinois_map(fig_width=14, fig_height=8):
    """
    Generates and saves the Illinois asthma hospitalization map.
    """
    try:
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Ensure Illinois boundary is loaded
        if illinois is None:
            st.warning("⚠️ Illinois county data is missing. Cannot generate the map.")
            return

        # Plot Illinois map with dynamic colors
        halo = unary_union(illinois.geometry).buffer(5000)
        halo_gs = gpd.GeoSeries([halo])
        halo_gs.plot(ax=ax, color=LINE_COLOR, edgecolor='none')

        illinois.plot(ax=ax, color=illinois["color"], edgecolor='darkgray')
        illinois.boundary.plot(ax=ax, edgecolor='gray', linewidth=1)

        # Label counties and place marker for Urban vs Rural
        for idx, row in illinois.iterrows():
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.text(cx, cy, row["name"], fontsize=6, ha='center', color='black')
            marker_offset = 5000
            if row["Urban_Rural"] == "Urban":
                ax.scatter(cx, cy - marker_offset, color='teal', s=20, marker='o')
            elif row["Urban_Rural"] == "Rural":
                ax.scatter(cx, cy - marker_offset, color='magenta', s=40, marker='*')

        # Add regional labels
        for region_name, (x, y, label) in region_labels.items():
            ax.text(
                x, y, str(label),
                fontsize=12, ha='center', va='center',
                color='white', fontweight='bold',
                path_effects=[withStroke(linewidth=3, foreground="black")]
            )

        # Save the figure
        OUTPUT_FOLDER = "static/maps"
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        map_filename = f"{OUTPUT_FOLDER}/{PARAM_RACE}_{PARAM_YEAR}.png"
        plt.savefig(map_filename, dpi=100, bbox_inches='tight')
        plt.close()  # Close figure to free memory

        # Display the generated map
        st.subheader(f"Generated Map for {PARAM_RACE.upper()} ({PARAM_YEAR})")
        st.image(map_filename, caption=f"Asthma Rates for {PARAM_RACE.upper()}, {PARAM_YEAR}", use_column_width=True)
        st.success(f"✅ Map successfully saved: `{map_filename}`")

    except Exception as e:
        st.error(f"❌ Error generating map: {e}")

# Run the function to generate and display the plot
plot_illinois_map(fig_width=14, fig_height=8)
