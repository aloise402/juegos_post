from flask import Flask, send_from_directory, jsonify
import json, os

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(".", "postemporada.html")

@app.route("/games_postseason.json")
def games_postseason():
    if os.path.exists("games_postseason.json"):
        with open("games_postseason.json", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "No hay datos"}), 404
