import os
import subprocess
from flask import Flask, request, send_file

app = Flask(__name__)

# Define folder for generated maps
OUTPUT_FOLDER = "static/maps"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Path to your full-featured map script
MAP_GENERATION_SCRIPT = r"F:\j45\userform for numerator\dashboard\v9_main_map.py"

@app.route('/update_map', methods=['GET'])
def update_map():
    """Generate and return the updated map based on user selection."""
    year = request.args.get('year', "2023")
    race = request.args.get('race', "NHA")

    # Define the expected map file path
    map_path = f"{OUTPUT_FOLDER}/{race}_{year}.png"

    # Delete old map to force regeneration
    if os.path.exists(map_path):
        os.remove(map_path)

    # Run the full-featured script with selected parameters
    try:
        subprocess.run(["python", MAP_GENERATION_SCRIPT, str(year), race], check=True)
    except subprocess.CalledProcessError as e:
        return f"Error generating map: {str(e)}", 500

    # Ensure the new map is created
    if not os.path.exists(map_path):
        return f"Error: Map '{map_path}' not found.", 404

    return send_file(map_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
