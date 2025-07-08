from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Variable global para almacenar la temperatura
current_temperature = {
    "value": 65.0,
    "timestamp": datetime.now().isoformat()
}

@app.route("/temperature", methods=["GET"])
def get_temperature():
    return jsonify(current_temperature)

@app.route("/temperature", methods=["POST"])
def update_temperature():
    data = request.get_json()
    if "value" in data:
        current_temperature["value"] = data["value"]
        current_temperature["timestamp"] = datetime.now().isoformat()
        return jsonify({"status": "updated", "temperature": current_temperature})
    else:
        return jsonify({"error": "Missing 'value' in request"}), 400
