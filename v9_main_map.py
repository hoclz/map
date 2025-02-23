# Set up the page configuration FIRST
import streamlit as st
st.set_page_config(
    page_title="Illinois Asthma Hospitalization",
    layout="centered",
    page_icon="📊"
)

# Now import other modules
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
import os

# Set Matplotlib backend
import matplotlib
matplotlib.use('Agg')

# Debugging: Check file paths
CSV_PATH = "Asthma_regional_data.csv"
COUNTY_TYPE_CSV = "county_type.csv"
TOTAL_COUNT_CSV = "total_count_per_race_ethnicity.csv"
IDPH_LOGO_PATH = "static/maps/IDPH_logo.png"  # Ensure this path is correct
ILLINOIS_GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/illinois-counties.geojson"

# File existence check (after st.set_page_config)
st.write("File Existence Check:")
st.write(f"CSV_PATH: {os.path.exists(CSV_PATH)}")
st.write(f"COUNTY_TYPE_CSV: {os.path.exists(COUNTY_TYPE_CSV)}")
st.write(f"TOTAL_COUNT_CSV: {os.path.exists(TOTAL_COUNT_CSV)}")
st.write(f"IDPH_LOGO_PATH: {os.path.exists(IDPH_LOGO_PATH)}")

# -------------------------------------------------------------------------
# 1) PARAMETERS (Updated for Streamlit)
# -------------------------------------------------------------------------
def plot_illinois_map():
    PARAM_YEAR = st.session_state.selected_year
    PARAM_RACE = st.session_state.selected_race

    st.write(f"Selected Year: {PARAM_YEAR}")
    st.write(f"Selected Race: {PARAM_RACE}")

    dynamic_line_color = {
        "NHB": "#E41A1C", "NHW": "#377EB8",
        "NHA": "#4DAF4A", "HISP": "#984EA3"
    }
    LINE_COLOR = dynamic_line_color[PARAM_RACE.upper()]


# -------------------------------------------------------------------------
# 2) READ & PREPARE THE ASTHMA DATA
# -------------------------------------------------------------------------
    df = pd.read_csv(CSV_PATH)
    rename_map = {
        "Group": "Race",
        "_2016": "2016", "_2017": "2017", "_2018": "2018",
        "_2019": "2019", "_2020": "2020", "_2021": "2021",
        "_2022": "2022", "_2023": "2023"
    }
    df = df.rename(columns=rename_map)

    year_cols = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    df_melted = df.melt(
        id_vars=["Race", "Region"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Rate"
    )
    df_melted["Year"] = df_melted["Year"].astype(int)

    df_filtered = df_melted[
        (df_melted["Year"] == PARAM_YEAR) &
        (df_melted["Race"].str.upper() == PARAM_RACE.upper())
    ]

    if df_filtered.empty:
        st.error(f"No data found for Race={PARAM_RACE}, Year={PARAM_YEAR}")
        return

    table_data = [[PARAM_RACE.upper()]]
    for _, row in df_filtered.iterrows():
        table_data.append([f"{row['Region']}, {row['Rate']}"])

    parsed = []
    for row in table_data[1:]:
        region, val = row[0].split(",", 1)
        parsed.append((region.strip(), float(val.strip())))
    parsed.sort(key=lambda x: x[1], reverse=True)
    table_data = [table_data[0]] + [[f"{r}, {v}"] for (r, v) in parsed]

    df_total_counts = pd.read_csv(TOTAL_COUNT_CSV).rename(columns=rename_map)
    total_row = df_total_counts[
        (df_total_counts["Race"].str.upper() == PARAM_RACE.upper()) &
        (df_total_counts["Region"].str.upper() == "TOTAL")
    ]
    TOTAL_COUNT = int(total_row[str(PARAM_YEAR)].iloc[0])

# -------------------------------------------------------------------------
# 3) BUILD THE CIRCLE VALUES
# -------------------------------------------------------------------------
    valid_circle_races = ["NHB", "NHW", "NHA", "HISP"]
    df_circle = df_melted[
        (df_melted["Year"] == PARAM_YEAR) &
        (df_melted["Region"].str.lower() == "statewide")
    ]
    circle_dict = {}
    for rc in valid_circle_races:
        row_rc = df_circle[df_circle["Race"].str.upper() == rc]
        if not row_rc.empty:
            circle_dict[rc] = str(row_rc["Rate"].iloc[0])

    selected_year = PARAM_YEAR

# -------------------------------------------------------------------------
# 4) READ & PREPARE GEOGRAPHY
# -------------------------------------------------------------------------
    illinois = gpd.read_file(ILLINOIS_GEOJSON_URL).to_crs(epsg=26971)
    state_boundary = illinois.dissolve()
    df_county_type = pd.read_csv(COUNTY_TYPE_CSV)
    illinois = illinois.merge(df_county_type, left_on="name", right_on="County", how="left")

    regions = {
        "NORTH": ["Boone", "Carroll", "Dekalb", "Jo Daviess", "Lee", "Ogle",
                 "Stephenson", "Whiteside", "Winnebago"],
        "NORTH-CENTRAL": ["Bureau", "Fulton", "Grundy", "Henderson", "Henry",
                         "Kendall", "Knox", "Lasalle", "Livingston", "Marshall",
                         "Mcdonough", "Mclean", "Mercer", "Peoria", "Putnam",
                         "Rock Island", "Stark", "Tazewell", "Warren", "Woodford"],
        "WEST-CENTRAL": ["Adams", "Brown", "Calhoun", "Cass", "Christian",
                        "Greene", "Hancock", "Jersey", "Logan", "Macoupin",
                        "Mason", "Menard", "Montgomery", "Morgan", "Pike",
                        "Sangamon", "Schuyler", "Scott"],
        "METRO EAST": ["Bond", "Clinton", "Madison", "Monroe", "Randolph",
                      "St. Clair", "Washington"],
        "SOUTHERN": ["Alexander", "Edwards", "Franklin", "Gallatin", "Hamilton",
                     "Hardin", "Jackson", "Jefferson", "Johnson", "Marion",
                     "Massac", "Perry", "Pope", "Pulaski", "Saline", "Union",
                     "Wabash", "Wayne", "White", "Williamson"],
        "EAST-CENTRAL": ["Champaign", "Clark", "Clay", "Coles", "Crawford",
                        "Cumberland", "Dewitt", "Douglas", "Edgar", "Effingham",
                        "Fayette", "Ford", "Iroquois", "Jasper", "Lawrence",
                        "Macon", "Moultrie", "Piatt", "Richland", "Shelby",
                        "Vermilion"],
        "SOUTH SUBURBAN": ["Kankakee", "Will"],
        "WEST SUBURBAN": ["Dupage", "Kane"],
        "NORTH SUBURBAN": ["Lake", "Mchenry"],
        "COOK": ["Cook"]
    }

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
        "COOK": (255/255, 255/255, 255/255)
    }

    illinois["Region"] = "Other"
    for region_name, county_list in regions.items():
        illinois.loc[illinois["name"].isin(county_list), "Region"] = region_name
    illinois["color"] = illinois["Region"].map(region_colors)

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
        "COOK": (1050000, 4600000, 10)
    }

    sources_text = f"""Sources
+ Population: Census Data, {PARAM_YEAR}
+ Asthma Count: Hospital Discharge Data, {PARAM_YEAR}
+ Urban/Rural: Illinois Department of Public Health (IDPH)
+ Region: https://graphics.chicagotribune.com/
  illinois-tier-mitigations/map-blurb.html"""

# -------------------------------------------------------------------------
# 5) HELPER FUNCTIONS
# -------------------------------------------------------------------------
    def add_image(ax, image_path, position, zoom):
        img = plt.imread(image_path)
        imagebox = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(imagebox, position, frameon=False, xycoords='axes fraction')
        ax.add_artist(ab)

    def add_illinois_outline(ax, boundary_gdf, position, zoom):
        inset_ax = fig.add_axes([position[0], position[1], zoom, zoom])
        boundary_gdf.boundary.plot(ax=inset_ax, linewidth=2, edgecolor=LINE_COLOR)
        inset_ax.axis('off')

    def draw_circle_with_cord(ax, center_x, center_y, radius, value, cord_x, cord_y, label="", highlight=False):
        angle = np.arctan2(cord_y - center_y, cord_x - center_x)
        contact_x = center_x + radius * np.cos(angle)
        contact_y = center_y + radius * np.sin(angle)
        circle = patches.Circle((center_x, center_y), radius, color=LINE_COLOR, fill=False, linewidth=1.5)
        ax.add_patch(circle)
        ax.text(center_x, center_y, value, ha="center", va="center", fontsize=9)
        text_props = {'ha': "center", 'va': "center", 'fontsize': 9}
        if highlight:
            ax.text(cord_x, cord_y + 0.15, label.upper(), **text_props, fontweight="bold")
        else:
            ax.text(cord_x, cord_y + 0.1, label.upper(), **text_props)
        ax.plot([cord_x, contact_x], [cord_y, contact_y], color=LINE_COLOR, linewidth=1)

    def draw_complete_diagram(ax, position):
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

        diagram_ax.plot([x_left, apex_x], [y_left, apex_y], color=LINE_COLOR, linewidth=2)
        diagram_ax.plot([apex_x, x_right], [apex_y, y_right], color=LINE_COLOR, linewidth=2)
        diagram_ax.plot([vertical_x, vertical_x], [apex_y, vertical_y], color=LINE_COLOR, linewidth=2)

        for i in range(fan_count):
            angle_offset = -fan_angle / 2 + i * (fan_angle / (fan_count - 1))
            x_fan = vertical_x + 0.3 * np.sin(np.radians(angle_offset))
            y_fan = vertical_y - 0.3 * np.cos(np.radians(angle_offset))
            diagram_ax.plot([vertical_x, x_fan], [vertical_y, y_fan], color=LINE_COLOR, linewidth=1)

        val_nhb = circle_dict["NHB"]
        val_nhw = circle_dict["NHW"]
        val_nha = circle_dict["NHA"]
        val_hisp = circle_dict["HISP"]

        draw_circle_with_cord(diagram_ax, (x_left+apex_x)/2, (y_left+apex_y)/2-0.3, circle_radius, val_nhb,
                             (x_left+apex_x)/2, (y_left+apex_y+0.03)/2, "NHB", PARAM_RACE=="NHB")
        draw_circle_with_cord(diagram_ax, (x_left+apex_x*2)/3, (y_left+apex_y*2)/3-0.4, circle_radius, val_nhw,
                             (x_left+apex_x*2)/3, (y_left+apex_y*2)/3, "NHW", PARAM_RACE=="NHW")
        draw_circle_with_cord(diagram_ax, (x_right+apex_x)/2, (y_right+apex_y)/2-0.3, circle_radius, val_nha,
                             (x_right+apex_x)/2, (y_right+apex_y)/2, "NHA", PARAM_RACE=="NHA")
        draw_circle_with_cord(diagram_ax, (x_right+apex_x*2)/3, (y_right+apex_y*2)/3-0.4, circle_radius, val_hisp,
                             (x_right+apex_x*2)/3, (y_right+apex_y*2)/3, "HISP", PARAM_RACE=="HISP")

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
            diagram_ax.text(apex_x + 1, y_legend_start - i*line_spacing, txt_line,
                           fontsize=9, ha="center", fontweight="bold" if rc==PARAM_RACE else "normal")

        diagram_ax.set_xlim(-length*scale_factor, length*scale_factor)
        diagram_ax.set_ylim(-length*scale_factor, (y_offset+length)*scale_factor)
        diagram_ax.set_aspect('equal')

        title_text = f"Statewide Asthma Age-Adjusted Rate Per 100,000\nby Race/Ethnicity ({selected_year})"
        title = diagram_ax.set_title(title_text, fontsize=9, y=1.05)
        if PARAM_RACE in title.get_text():
            title.set_bbox(dict(facecolor="yellow", alpha=0.8, edgecolor="none"))

# -------------------------------------------------------------------------
# 6) PLOT ILLINOIS MAP
# -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 8))

    # Map halo
    halo = unary_union(illinois.geometry).buffer(5000)
    gpd.GeoSeries([halo]).plot(ax=ax, color=LINE_COLOR, edgecolor='none')

    # Main map
    illinois.plot(ax=ax, color=illinois["color"], edgecolor='darkgray')
    illinois.boundary.plot(ax=ax, edgecolor='gray', linewidth=1)

    # County labels and markers
    for idx, row in illinois.iterrows():
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        ax.text(cx, cy, row["name"], fontsize=6, ha='center', color='black')
        marker_offset = 5000
        if row["Urban_Rural"] == "Urban":
            ax.scatter(cx, cy - marker_offset, color='teal', s=20, marker='o')
        elif row["Urban_Rural"] == "Rural":
            ax.scatter(cx, cy - marker_offset, color='magenta', s=40, marker='*')

    # Region labels
    for region_name, (x, y, label) in region_labels.items():
        ax.text(x, y, str(label), fontsize=12, ha='center', va='center',
               color='white', fontweight='bold',
               path_effects=[withStroke(linewidth=3, foreground="black")])

    # Legends
    region_legend = ax.legend(
        handles=[Patch(facecolor=c, edgecolor='black', label=l) for l, c in region_colors.items()],
        loc='upper left', bbox_to_anchor=(0.75, 0.90), title='Regions',
        fontsize=8, title_fontsize=10
    )
    ax.add_artist(region_legend)

    county_legend = ax.legend(
        handles=[
            Line2D([0], [0], marker='o', color='w', label='Urban',
                  markerfacecolor='teal', markersize=8),
            Line2D([0], [0], marker='*', color='w', label='Rural',
                  markerfacecolor='magenta', markersize=12)
        ],
        loc='upper right', bbox_to_anchor=(0.75, 0.90), title='County Type',
        fontsize=10, title_fontsize=10
    )

    # Data table
    table_ax = fig.add_axes([0.28, 0.38, 0.12, 0.4])
    table_ax.axis("off")
    tab = Table(table_ax, bbox=[0, 0, 1, 1])
    for i, row in enumerate(table_data):
        cell = tab.add_cell(i, 0, width=2.5, height=0.8, text=row[0],
                          loc='center', facecolor='white', edgecolor='black')
        cell.set_text_props(fontweight='bold' if i == 0 else 'normal')

    # Sources text
    text_ax = fig.add_axes([0.277, 0.125, 0.22, 0.2])
    text_ax.axis("off")
    text_ax.text(0, 1, sources_text, transform=text_ax.transAxes,
                fontsize=9, va="top", ha="left", linespacing=1.5)

    # IDPH logo
    add_image(ax, IDPH_LOGO_PATH, (0.35, 0.07), 0.25)

    # Illinois outline
    add_illinois_outline(ax, state_boundary, (0.63, 0.65), 0.057)

    # Total count
    ax.text(0.70, 0.74, f"T={TOTAL_COUNT}", transform=ax.transAxes,
           fontsize=9, color='black', ha='left', va='center')

    # Funnel diagram
    draw_complete_diagram(ax, [0.64, 0.03, 0.15, 0.5])

    # Main title
    race_descriptions = {
        "NHB": "Non-Hispanic Black",
        "NHW": "Non-Hispanic White",
        "NHA": "Non-Hispanic Asian",
        "HISP": "Hispanic"
    }
    title_text = (f"Regional Asthma Age-Adjusted Rates Per 100,000 HOSPITALIZATION Discharges\n"
                 f"for {race_descriptions[PARAM_RACE]} ({PARAM_RACE}) Population, {PARAM_YEAR}")
    ax.set_title(title_text, fontsize=12, y=1.05)
    ax.set_axis_off()

# -------------------------------------------------------------------------
# 7) RENDER IN STREAMLIT
# -------------------------------------------------------------------------
    st.pyplot(fig)
    plt.close()

# -------------------------------------------------------------------------
# 8) RUN THE PLOT
# -------------------------------------------------------------------------
def main():
    st.title("Illinois Asthma Hospitalization Dashboard")
    # Add your Streamlit components here
    plot_illinois_map()

if __name__ == "__main__":
    main()
