from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# URL del Worker (ajusta con el subdominio real de Render)
WORKER_URL = os.getenv("WORKER_URL", "https://tu-worker.onrender.com/api/cache")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/full")
def api_full():
    try:
        r = requests.get(WORKER_URL, timeout=15)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": f"No se pudo leer del worker: {e}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=True)
