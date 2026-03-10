import matplotlib
matplotlib.use ('Agg')
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
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            return jsonify({"error": "No hay datos"}), 404

        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce')
        df = df.dropna(subset=['timestamp'])
        
        if df.empty:
            return jsonify({"error": "Sin datos válidos"}), 404

        # 7 días de datos
        ahora = pd.Timestamp.now()
        hace_7d = ahora - pd.Timedelta(days=7)
        df_filtrado = df[df['timestamp'] >= hace_7d]
        
        if df_filtrado.empty:
            return jsonify({"error": "Sin datos recientes"}), 404

        # ¡SIN resample! Todos los puntos
        plt.figure(figsize=(14, 6))
        plt.plot(df_filtrado['timestamp'], df_filtrado['valor_sensor'], 
                 'o-', color='orange', markersize=6, linewidth=2, label='Temperatura')
        plt.title("Temperatura - Últimos 7 días")
        plt.xlabel("Hora")
        plt.ylabel("°C")
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/datos", methods=["GET"])
def ver_datos():
    """Ver todos los datos del CSV"""
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({"error": "CSV no existe"}), 404
        
        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Devolver JSON con últimos 50 registros
        datos_json = df.tail(50).to_dict('records')
        
        return jsonify({
            "total_registros": len(df),
            "datos": datos_json
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)  # debug=False en producción
