from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import io

app = Flask(__name__)

current_temperature = {
    "value": 25.0,
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

@app.route("/grafico", methods=["GET"])
def grafico_temperatura():
    # Leer datos reales desde un archivo CSV
    df = pd.read_csv('datos_sensor.csv', parse_dates=['timestamp'])

    # Filtrar solo las últimas 24 horas
    ahora = datetime.now()
    hace_24h = ahora - timedelta(hours=24)
    df_filtrado = df[df['timestamp'] >= hace_24h]

    # Re-muestrear cada 15 minutos (por si hay más datos)
    df_filtrado.set_index('timestamp', inplace=True)
    df_15min = df_filtrado.resample('15T').mean()

    # Crear el gráfico
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
    app.run(debug=True)
