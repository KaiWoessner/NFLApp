from __future__ import annotations

import os

from flask import Flask, jsonify, request

from nfl_data_service import (
    LATEST_COMPLETED_SEASON,
    MAX_RANKINGS_SEASON,
    MIN_SEASON,
    get_game_details_payload,
    get_games_payload,
    get_meta_payload,
    get_rankings_payload,
)


app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/api/meta", methods=["GET"])
def meta():
    return jsonify(get_meta_payload())


@app.route("/api/games", methods=["GET"])
def games():
    view_mode = request.args.get("viewMode", "all_games")
    start_season = int(request.args.get("startSeason", MIN_SEASON))
    end_season = int(request.args.get("endSeason", LATEST_COMPLETED_SEASON))
    page = int(request.args.get("page", 1))
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if start_season < MIN_SEASON or end_season > LATEST_COMPLETED_SEASON or start_season > end_season:
        return jsonify({"error": "Invalid season range."}), 400

    payload, status = get_games_payload(
        view_mode=view_mode,
        start_season=start_season,
        end_season=end_season,
        team1=team1,
        team2=team2,
        page=page,
    )
    return jsonify(payload), status


@app.route("/api/game-details", methods=["POST", "OPTIONS"])
def game_details():
    if request.method == "OPTIONS":
        return ("", 204)

    payload = request.get_json(silent=True) or {}
    selected_game = payload.get("selectedGame")
    if not selected_game:
        return jsonify({"error": "A selected game payload is required."}), 400

    response_payload, status = get_game_details_payload(
        selected_game=selected_game,
        team1=payload.get("team1"),
        team2=payload.get("team2"),
    )
    return jsonify(response_payload), status


@app.route("/api/rankings", methods=["GET"])
def rankings():
    season = int(request.args.get("season", MAX_RANKINGS_SEASON))
    if season < MIN_SEASON or season > MAX_RANKINGS_SEASON:
        return jsonify({"error": "Invalid rankings season."}), 400

    payload, status = get_rankings_payload(season)
    return jsonify(payload), status


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5001")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
