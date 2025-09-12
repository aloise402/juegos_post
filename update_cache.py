# update_cache.py
from flask import Flask, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
import standings_cascade_points_desc as standings

app = Flask(__name__)
SCL = ZoneInfo("America/Santiago")

@app.route("/api/cache")
def api_cache():
    ts = datetime.now(SCL).strftime('%Y-%m-%d %H:%M:%S')

    try:
        rows = standings.compute_rows() or []
        games_today = standings.games_played_today_scl() or []

        payload = {
            "standings": rows,
            "games_today": games_today,
            "last_updated": ts
        }
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # corre en el puerto que Render asigne
    import os
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
