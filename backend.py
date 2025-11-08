import json
import subprocess
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__, static_folder='./frontend/calendar-app/build', static_url_path='/')
# CORS(app, resources={r"/*": {"origins": "*"}}) -> used to debug CORS issues

# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    print("Requested path:", path)
    build_path = Path(app.static_folder)
    requested_file = build_path / path

    if path != "" and requested_file.exists():
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
    
    
@app.route('/schedule', methods=['POST'])
def run_schedule():
    """
    Expects JSON payload:
    {
        "schedule": {...},
        "overrides": [...],
        "from": "2025-11-07T17:00:00Z",
        "until": "2025-11-21T17:00:00Z"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    schedule_data = data.get("schedule")
    overrides_data = data.get("overrides", [])
    from_str = data.get("from")
    until_str = data.get("until")
    
    print("Received schedule data:", schedule_data)
    print("Received overrides data:", overrides_data)
    print("From:", from_str)
    print("Until:", until_str)

    if not schedule_data or not from_str or not until_str:
        return jsonify({"error": "Missing required parameters: schedule, from, until"}), 400

    # Save JSON files locally
    try:
        with open("schedule.json", "w") as f:
            json.dump(schedule_data, f, indent=2)
        with open("overrides.json", "w") as f:
            json.dump(overrides_data, f, indent=2)
    except Exception as e:
        return jsonify({"error": f"Failed to write JSON files: {e}"}), 500

    # Run the CLI command
    cmd = [
        "./render-schedule.py",
        f"--schedule=schedule.json",
        f"--overrides=overrides.json",
        f"--from={from_str}",
        f"--until={until_str}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "render-schedule.py failed",
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500

    # Read the output.json
    try:
        with open("output.json", "r") as f:
            output = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to read output.json: {e}"}), 500

    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True, port=5500)
