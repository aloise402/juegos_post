# ==========================
# update_cache_post.py
# ==========================
# Usa la MISMA base/lógica de temporada regular (standings_cascade_points_desc),
# pero NO calcula/imprime posiciones. En su lugar:
#   - Acumula TODOS los juegos jugados por miembros de la liga
#     entre START_DATE_SCL y END_DATE_SCL (fechas locales Chile)
#   - Genera games_postseason.json
# ==========================

import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

import standings_cascade_points_desc as standings  # ♥ usa fielmente tus utilidades/base  :contentReference[oaicite:2]{index=2}

# === Config Postemporada (fechas locales Chile) ===
START_DATE_SCL = date(2025, 9, 9)   # 09-09-2025
END_DATE_SCL   = date(2025, 9, 21)  # 21-09-2025
OUTPUT_FILE    = "games_postseason.json"

def games_between_scl(start_d: date, end_d: date):
    """
    Reutiliza la misma captura de páginas y filtros del módulo de temporada regular:
      - MODE = "LEAGUE"
      - Dedup por id + clave canónica
      - Ambos participantes deben pertenecer a la liga (mismo criterio que usas)
      - Convertimos fechas a America/Santiago y filtramos por rango [start_d, end_d]
    """
    tz_scl = ZoneInfo("America/Santiago")
    tz_utc = ZoneInfo("UTC")

    # 1) Traer páginas de TODOS los usuarios definidos en LEAGUE_ORDER, igual que en regular
    all_pages = []
    for username_exact, _team in standings.LEAGUE_ORDER:
        for p in standings.PAGES:
            all_pages += standings.fetch_page(username_exact, p)

    # 2) Deduplicación
    pages = standings.dedup_by_id(all_pages)

    seen_ids = set()
    seen_keys = set()
    items = []

    for g in pages:
        # a) Modo de juego fiel (LEAGUE)
        if (g.get("game_mode") or "").strip().upper() != standings.MODE:
            continue

        # b) Parse + TZ (misma lógica: parse display_date, asumir UTC si naive, convertir a SCL)
        d = standings.parse_date(g.get("display_date", ""))
        if not d:
            continue
        if d.tzinfo is None:
            d = d.replace(tzinfo=tz_utc)
        d_local = d.astimezone(tz_scl)

        # c) Rango de fechas locales Chile
        if not (start_d <= d_local.date() <= end_d):
            continue

        # d) Miembros de la liga (exactamente el filtro que usas: ambos miembros)
        home_name_raw = (g.get("home_name") or "")
        away_name_raw = (g.get("away_name") or "")
        h_norm = standings.normalize_user_for_compare(home_name_raw)
        a_norm = standings.normalize_user_for_compare(away_name_raw)
        if not (h_norm in standings.LEAGUE_USERS_NORM and a_norm in standings.LEAGUE_USERS_NORM):
            continue

        # e) Dedup por id y clave canónica robusta (misma idea que en "hoy")
        gid = str(g.get("id") or "")
        if gid and gid in seen_ids:
            continue

        home = (g.get("home_full_name") or "").strip()
        away = (g.get("away_full_name") or "").strip()
        hr = int(g.get("home_runs") or 0)
        ar = int(g.get("away_runs") or 0)
        pitcher_info = (g.get("display_pitcher_info") or "").strip()

        canon_key = (home, away, hr, ar, pitcher_info)
        if canon_key in seen_keys:
            continue

        if gid:
            seen_ids.add(gid)
        seen_keys.add(canon_key)

        # f) Salida normalizada (incluye fecha UTC y local SCL)
        out = {
            "id": gid,
            "date_local_scl": d_local.strftime("%Y-%m-%d %H:%M:%S"),
            "date_utc": d.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S%z"),
            "home": home,
            "away": away,
            "home_runs": hr,
            "away_runs": ar,
            "home_user": home_name_raw,
            "away_user": away_name_raw,
            "pitcher_info": pitcher_info,
        }
        items.append((d_local, out))

    # Orden cronológico
    items.sort(key=lambda x: x[0])
    return [x[1] for x in items]

def main():
    games = games_between_scl(START_DATE_SCL, END_DATE_SCL)
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "range_local_scl": {
            "start": START_DATE_SCL.strftime("%Y-%m-%d"),
            "end": END_DATE_SCL.strftime("%Y-%m-%d")
        },
        "count": len(games),
        "items": games
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"✅ Postemporada: {len(games)} juegos guardados en {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
