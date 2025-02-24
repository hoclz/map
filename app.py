import os
import subprocess
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

# Define the folder for generated maps
OUTPUT_FOLDER = os.path.join(os.getcwd(), "static/maps")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Correct path to the main map script
MAP_GENERATION_SCRIPT = os.path.join(os.getcwd(), "v9_main_map.py")

@app.route('/update_map', methods=['GET'])
def update_map():
    """Generate and return the updated map based on user selection."""
    year = request.args.get('year', "2023")
    race = request.args.get('race', "NHA").upper()  # Ensure uppercase for dataset consistency

    # Define expected map file path
    map_path = os.path.join(OUTPUT_FOLDER, f"{race}_{year}.png")

    # Remove old map if it exists to force regeneration
    if os.path.exists(map_path):
        os.remove(map_path)

    # Run the main map script with parameters
    try:
        result = subprocess.run(
            ["python", MAP_GENERATION_SCRIPT, str(year), race],
            check=True,
            capture_output=True,
            text=True
        )
        print("Map Generation Output:", result.stdout)
        print("Map Generation Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Map generation failed", "details": str(e)}), 500

    # Ensure the new map is created
    if not os.path.exists(map_path):
        return jsonify({"error": f"Map '{map_path}' not found."}), 404

    return send_file(map_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
