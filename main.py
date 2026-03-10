from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import traceback

app = Flask(__name__)
CSV_FILE = 'datos_sensor.csv'

@app.route("/temperature", methods=["POST"])
def update_temperature():
    try:
        data = request.get_json()
        if not data or "value" not in data:
            return jsonify({"error": "Missing 'value' in request"}), 400
        
        # Convertir value a float para evitar problemas
        try:
            value = float(data["value"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid 'value' format"}), 400
        
        timestamp = datetime.now().isoformat()
        new_row = pd.DataFrame([{
            "timestamp": timestamp,
            "valor_sensor": value
        }])
        
        # Guardar de forma más robusta
        if os.path.exists(CSV_FILE):
            # Leer datos existentes, agregar nuevo, guardar todo
            df = pd.read_csv(CSV_FILE, parse_dates=['timestamp'])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
        else:
            new_row.to_csv(CSV_FILE, index=False)
        
        return jsonify({"status": "updated", "timestamp": timestamp, "value": value}), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/grafico", methods=["GET"])
def grafico_temperatura():
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({"error": "No hay datos registrados"}), 404

        # Leer datos con manejo de errores
        df = pd.read_csv(CSV_FILE, parse_dates=['timestamp'])
        if df.empty:
            return jsonify({"error": "Archivo vacío"}), 404

        # Filtrar últimas 24 horas
        ahora = datetime.now()
        hace_24h = ahora - timedelta(hours=24)
        df_filtrado = df[df['timestamp'] >= hace_24h]
        
        if df_filtrado.empty:
            return jsonify({"error": "No hay datos en las últimas 24 horas"}), 404

        # Re-muestrear cada 15 minutos
        df_filtrado.set_index('timestamp', inplace=True)
        df_15min = df_filtrado.resample('15T').mean().dropna()

        if df_15min.empty:
            return jsonify({"error": "No hay datos suficientes para graficar"}), 404

        # Crear gráfica
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df_15min.index, df_15min['valor_sensor'], 
                marker='o', color='orange', linestyle='-', linewidth=2, markersize=4)
        ax.set_title("Temperatura - Últimas 24 horas (cada 15 min)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hora", fontsize=12)
        ax.set_ylabel("Temperatura (°C)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    """Página de inicio para evitar 404"""
    return jsonify({
        "message": "API Temperatura funcionando",
        "endpoints": {
            "POST /temperature": "Enviar temperatura (JSON: {\"value\": 23.5})",
            "GET /grafico": "Obtener gráfica PNG últimas 24h"
        }
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
