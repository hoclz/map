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
import sys

# Read parameters from command line (Flask will pass these)
PARAM_YEAR = int(sys.argv[1])  # Year input from Flask
PARAM_RACE = sys.argv[2]  # Race input from Flask


# -------------------------------------------------------------------------
# 1) PARAMETERS
# -------------------------------------------------------------------------
CSV_PATH = "Asthma_regional_data.csv"
COUNTY_TYPE_CSV = "county_type.csv"
ILLINOIS_GEOJSON_URL = (
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/illinois-counties.geojson"
)

# PARAM_YEAR = 2023
# PARAM_RACE = "NHA"   # Must be one of: "NHB", "NHW", "NHA", "HISP"

# Path to the CSV containing the TOTAL counts per race/year
TOTAL_COUNT_CSV = "total_count_per_race_ethnicity.csv"  

# Define a dictionary of high-contrast colors for the dynamic line color
dynamic_line_color = {
    "NHB": "#E41A1C",   # Red
    "NHW": "#377EB8",   # Blue
    "NHA": "#4DAF4A",   # Green
    "HISP": "#984EA3"   # Purple
}
LINE_COLOR = dynamic_line_color[PARAM_RACE.upper()]

# -------------------------------------------------------------------------
# 2) READ & PREPARE THE ASTHMA DATA
# -------------------------------------------------------------------------
df = pd.read_csv(CSV_PATH)

rename_map = {
    "Group": "Race",
    "_2016": "2016",
    "_2017": "2017",
    "_2018": "2018",
    "_2019": "2019",
    "_2020": "2020",
    "_2021": "2021",
    "_2022": "2022",
    "_2023": "2023",
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
    raise ValueError(
        f"No rows found for Race={PARAM_RACE}, Year={PARAM_YEAR}. "
        "Check your CSV or parameters."
    )

# Build table_data: first row = Race acronym, then "Region, Rate" rows
table_data = []
table_data.append([PARAM_RACE.upper()])
for _, row in df_filtered.iterrows():
    region_str = str(row["Region"])
    rate_val = str(row["Rate"])
    table_data.append([f"{region_str}, {rate_val}"])

# (NEW) 2.5) Sort table rows descending by numeric rate
header = table_data[0]
data_rows = table_data[1:]

parsed = []
for row_item in data_rows:
    row_str = row_item[0]
    region, val_str = row_str.split(",", 1)
    region = region.strip()
    val_str = val_str.strip()
    val = float(val_str)
    parsed.append((region, val))

parsed.sort(key=lambda x: x[1], reverse=True)
table_data = [header] + [[f"{r}, {v}"] for (r, v) in parsed]

# (NEW) 2.6) LOAD & GET THE TOTAL COUNT DYNAMICALLY
df_total_counts = pd.read_csv(TOTAL_COUNT_CSV)
rename_map_for_total = {
    "Group": "Race",
    "Region": "Region",
    "_2016": "2016",
    "_2017": "2017",
    "_2018": "2018",
    "_2019": "2019",
    "_2020": "2020",
    "_2021": "2021",
    "_2022": "2022",
    "_2023": "2023",
}
df_total_counts = df_total_counts.rename(columns=rename_map_for_total)
df_total_counts_filtered = df_total_counts[
    (df_total_counts["Race"].str.upper() == PARAM_RACE.upper()) &
    (df_total_counts["Region"].str.upper() == "TOTAL")
]
if df_total_counts_filtered.empty:
    raise ValueError(
        f"No total count found for Race={PARAM_RACE}, Year={PARAM_YEAR} in {TOTAL_COUNT_CSV}."
    )
TOTAL_COUNT = int(df_total_counts_filtered[str(PARAM_YEAR)].iloc[0])

# -------------------------------------------------------------------------
# 3) BUILD THE CIRCLE VALUES FROM "statewide" ROWS (for each race)
# -------------------------------------------------------------------------
valid_circle_races = ["NHB", "NHW", "NHA", "HISP"]
df_circle = df_melted[
    (df_melted["Year"] == PARAM_YEAR) &
    (df_melted["Region"].str.lower() == "statewide")
]
circle_dict = {}
for rc in valid_circle_races:
    row_rc = df_circle[df_circle["Race"].str.upper() == rc]
    if row_rc.empty:
        raise ValueError(
            f"No 'statewide' row found for race '{rc}' in year {PARAM_YEAR}."
        )
    circle_dict[rc] = str(row_rc["Rate"].iloc[0])

selected_year = PARAM_YEAR

# -------------------------------------------------------------------------
# 4) READ & PREPARE THE ILLINOIS COUNTY GEOMETRY
# -------------------------------------------------------------------------
illinois = gpd.read_file(ILLINOIS_GEOJSON_URL).to_crs(epsg=26971)
state_boundary = illinois.dissolve()

df_county_type = pd.read_csv(COUNTY_TYPE_CSV)
illinois = illinois.merge(df_county_type, left_on="name", right_on="County", how="left")

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

illinois["Region"] = "Other"
for region_name, county_list in regions.items():
    illinois.loc[illinois["name"].isin(county_list), "Region"] = region_name

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
    if highlight:
        ax.text(
            cord_x, cord_y + 0.15, label.upper(),
            ha="center", va="center", fontsize=9,
            fontweight="bold"
        )
    else:
        ax.text(cord_x, cord_y + 0.1, label.upper(), ha="center", va="center", fontsize=9)
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

    val_nhb = circle_dict["NHB"]
    val_nhw = circle_dict["NHW"]
    val_nha = circle_dict["NHA"]
    val_hisp = circle_dict["HISP"]

    # NHB
    draw_circle_with_cord(
        diagram_ax,
        (x_left + apex_x) / 2,
        (y_left + apex_y) / 2 - 0.3,
        circle_radius,
        val_nhb,
        (x_left + apex_x) / 2,
        (y_left + apex_y + 0.03) / 2,
        label="NHB",
        highlight=(PARAM_RACE.upper() == "NHB")
    )
    # NHW
    draw_circle_with_cord(
        diagram_ax,
        (x_left + apex_x * 2) / 3,
        (y_left + apex_y * 2) / 3 - 0.4,
        circle_radius,
        val_nhw,
        (x_left + apex_x * 2) / 3,
        (y_left + apex_y * 2) / 3,
        label="NHW",
        highlight=(PARAM_RACE.upper() == "NHW")
    )
    # NHA
    draw_circle_with_cord(
        diagram_ax,
        (x_right + apex_x) / 2,
        (y_right + apex_y) / 2 - 0.3,
        circle_radius,
        val_nha,
        (x_right + apex_x) / 2,
        (y_right + apex_y) / 2,
        label="NHA",
        highlight=(PARAM_RACE.upper() == "NHA")
    )
    # HISP
    draw_circle_with_cord(
        diagram_ax,
        (x_right + apex_x * 2) / 3,
        (y_right + apex_y * 2) / 3 - 0.4,
        circle_radius,
        val_hisp,
        (x_right + apex_x * 2) / 3,
        (y_right + apex_y * 2) / 3,
        label="HISP",
        highlight=(PARAM_RACE.upper() == "HISP")
    )

    # Instead of a single text block, do multiple lines.
    legend_items = {
        "NHA": "Non-Hispanic Asian",
        "NHB": "Non-Hispanic Black",
        "NHW": "Non-Hispanic White",
        "HISP": "Hispanic"
    }
    y_legend_start = vertical_y + 0.6
    line_spacing = 0.3
    i = 0
    for rc, desc in legend_items.items():
        txt_line = f"{rc} = {desc}"
        if rc == PARAM_RACE.upper():
            diagram_ax.text(
                apex_x + 1, 
                y_legend_start - i*line_spacing,
                txt_line,
                fontsize=9,
                ha="center",
                fontweight="bold",
                color="black"  # Bold red for the selected race
            )
        else:
            diagram_ax.text(
                apex_x + 1, 
                y_legend_start - i*line_spacing,
                txt_line,
                fontsize=9,
                ha="center",
                fontweight="normal"
            )
        i += 1

    diagram_ax.set_xlim(-length * scale_factor, length * scale_factor)
    diagram_ax.set_ylim(-length * scale_factor, (y_offset + length) * scale_factor)
    diagram_ax.set_aspect('equal', adjustable='box')

    diagram_title_obj = plt.title(
        f"Statewide Asthma Age-Adjusted Rate Per 100,000  \nby Race/Ethnicity ({selected_year}) ",
        fontsize=9, y=1.05
    )
    if PARAM_RACE.upper() in diagram_title_obj.get_text().upper():
        diagram_title_obj.set_bbox(dict(facecolor="yellow", alpha=0.8, edgecolor="none"))
def plot_illinois_map(fig_width, fig_height):
    global fig
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Apply dynamic line color to the map halo
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

    for region_name, (x, y, label) in region_labels.items():
        ax.text(
            x, y, str(label),
            fontsize=12, ha='center', va='center',
            color='white', fontweight='bold',
            path_effects=[withStroke(linewidth=3, foreground="black")]
        )

    region_legend_elements = [
        Patch(facecolor=color, edgecolor='black', label=rgn)
        for rgn, color in region_colors.items()
    ]
    region_legend = ax.legend(
        handles=region_legend_elements,
        loc='upper left',
        bbox_to_anchor=(0.75, 0.90),
        title='Regions',
        fontsize=8,
        title_fontsize=10,
        frameon=True
    )
    ax.add_artist(region_legend)

    county_type_legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Urban', markerfacecolor='teal', markersize=8),
        Line2D([0], [0], marker='*', color='w', label='Rural', markerfacecolor='magenta', markersize=12)
    ]
    ax.legend(
        handles=county_type_legend_elements,
        loc='upper right',
        bbox_to_anchor=(0.75, 0.90),
        title='County Type',
        fontsize=10,
        title_fontsize=10,
        frameon=True
    )

    # TABLE (#4) from table_data (already sorted)
    table_ax = fig.add_axes([0.28, 0.38, 0.12, 0.4])  #  adjusting the width (3rd) value will increase the fontsize too
    table_ax.axis("off")
    tab = Table(table_ax, bbox=[0, 0, 1, 1])

    cell_width = 2.5
    cell_height = 0.8

    for i, row_vals in enumerate(table_data):
        for j, cell_val in enumerate(row_vals):
            facecol = "white"
            cell = tab.add_cell(
                i, j,
                width=cell_width,
                height=cell_height,
                text=cell_val,
                loc='center',
                facecolor=facecol,
                edgecolor="black"
            )
            if i == 0 or PARAM_RACE.upper() in cell_val.upper():
                cell.set_text_props(fontweight='bold')
            else:
                cell.set_text_props(fontweight='normal')

    table_ax.add_table(tab)

    # SOURCES TEXT (#5)
    text_ax = fig.add_axes([0.277, 0.125, 0.22, 0.2])
    text_ax.axis("off")
    text_ax.text(
        0, 1, sources_text,
        transform=text_ax.transAxes,
        fontsize=9, color="black",
        va="top", ha="left",
        linespacing=1.5
    )

    # IDPH LOGO (#6)
    add_image(ax, r"F:\j45\userform for numerator\dashboard\IDPH_logo.png", (0.35, 0.07), zoom=0.25)

    # SMALL ILLINOIS OUTLINE (#9)
    add_illinois_outline(ax, state_boundary, position=(0.63, 0.65), zoom=0.057)

    # T=TOTAL_COUNT (#10)
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
    draw_complete_diagram(ax, [0.64, 0.03, 0.15, 0.5])

    # FINAL TITLE (#2) using Two Separate Text Calls for Partial Bold
    race_descriptions = {
        "NHB": "Non-Hispanic Black",
        "NHW": "Non-Hispanic White",
        "NHA": "Non-Hispanic Asian",
        "HISP": "Hispanic",
    }
    full_text = race_descriptions.get(PARAM_RACE.upper(), "Unknown Race")

    # Main title without the acronym (with extra space to insert it)
    # Define dynamic color for the second part of the title
    race_colors = {
        "NHB": "black",      # Non-Hispanic Black
        "NHW": "black",       # Non-Hispanic White
        "NHA": "black",      # Non-Hispanic Asian
        "HISP": "black"        # Hispanic
    }
    title_color = race_colors.get(PARAM_RACE.upper(), "black")
    
    # Ensure proper spacing between words
    formatted_full_text = full_text.replace(" ", " ")  # Non-breaking spaces
    
    # Define title components
    title_part1 = "Regional Asthma Age-Adjusted Rates Per 100,000 HOSPITALIZATION Discharges for"
    title_part2 = f"{formatted_full_text} ({PARAM_RACE.upper()})"
    title_part3 = f"Population, {selected_year}"

    
    # Ensure spaces appear correctly
    title_str = (
        f"{title_part1} "
        f"$\\mathbf{{ {formatted_full_text} \\ ({PARAM_RACE.upper()}) }}$ "  # Explicit spacing
        f"{title_part3}"
    )
    
    # Apply the title with adjusted position
    ax.set_title(title_str, fontsize=12, color=title_color, fontweight="normal", x=0.54, y=1.05)


    ax.set_aspect('equal', adjustable='datalim')
    ax.set_axis_off()

    # Save the figure as a PNG or PDF (choose one)
    plt.savefig(f"{PARAM_RACE.upper()}_AgeAdjustedRate_{PARAM_YEAR}.png", dpi=100)
    # plt.savefig(f"{PARAM_RACE.upper()}_AgeAdjustedRate_{PARAM_YEAR}.pdf", dpi=300)
    plt.show()

# -------------------------------------------------------------------------
# 7) RUN THE PLOT
# -------------------------------------------------------------------------
plot_illinois_map(fig_width=14, fig_height=8)

# Ensure the directory exists
OUTPUT_FOLDER = "static/maps"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Define the file path
map_filename = f"{OUTPUT_FOLDER}/{PARAM_RACE}_{PARAM_YEAR}.png"

# Save the image
plt.savefig(map_filename, dpi=100)
plt.close()  # Ensure Matplotlib releases memory

print(f"✅ Map successfully saved at: {map_filename}")
