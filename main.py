from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

CSV_FILE = 'datos_sensor.csv'

@app.route("/temperature", methods=["POST"])
def update_temperature():
    data = request.get_json()
    if "value" in data:
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

@app.route("/grafico", methods=["GET"])
def grafico_temperatura():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "No hay datos registrados"}), 404

    # Leer los datos guardados
    df = pd.read_csv(CSV_FILE, parse_dates=['timestamp'])

    # Filtrar las últimas 24 horas
    ahora = datetime.now()
    hace_24h = ahora - timedelta(hours=24)
    df_filtrado = df[df['timestamp'] >= hace_24h]

    # Re-muestrear cada 15 minutos (por si hay más datos)
    df_filtrado.set_index('timestamp', inplace=True)
    df_15min = df_filtrado.resample('15T').mean()

    # Crear la gráfica
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_15min.index, df_15min['valor_sensor'], marker='o', color='orange', linestyle='-')
    ax.set_title("Temperatura ACS - Últimas 24 horas (cada 15 minutos)")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True)
    fig.autofmt_xdate()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
