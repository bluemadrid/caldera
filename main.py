from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import io

app = Flask(__name__)

# Variable global para almacenar la temperatura actual
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

@app.route("/grafico", methods=["GET"])
def grafico_temperatura():
    # Simular datos de temperatura para las últimas 24 horas
    horas = [datetime.now() - timedelta(hours=i) for i in reversed(range(24))]
    temperaturas = np.random.normal(loc=65, scale=2, size=24)

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(horas, temperaturas, marker='o', color='orange', linestyle='-')
    ax.set_title("Temperatura ACS - Últimas 24 horas")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True)
    fig.autofmt_xdate()

    # Guardar el gráfico en un buffer de memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    # Enviar la imagen como respuesta
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
