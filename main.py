from flask import Flask, request, jsonify
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)

CSV_FILE = 'datos_sensor.csv'

@app.route("/temperature", methods=["POST"])
def update_temperature():
    data = request.get_json()
    if "value" in data:
        # Registrar nueva lectura en el archivo CSV
        timestamp = datetime.now().isoformat()
        new_row = pd.DataFrame([{
            "timestamp": timestamp,
            "valor_sensor": data["value"]
        }])
        if os.path.exists(CSV_FILE):
            new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)
        else:
            new_row.to_csv(CSV_FILE, mode='w', header=True, index=False)
        return jsonify({"status": "updated", "timestamp": timestamp, "value": data["value"]})
    else:
        return jsonify({"error": "Missing 'value' in request"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
