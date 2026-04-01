from datetime import datetime
import time
from io import BytesIO
import urllib.request
from urllib.parse import urlencode

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

try:
    import nflreadpy as nfl
except ImportError:
    nfl = None


st.set_page_config(page_title="NFL Game Explorer", layout="wide")
TEAM_LOGO_SLUGS = {
    "ARI": "ari",
    "ATL": "atl",
    "BAL": "bal",
    "BUF": "buf",
    "CAR": "car",
    "CHI": "chi",
    "CIN": "cin",
    "CLE": "cle",
    "DAL": "dal",
    "DEN": "den",
    "DET": "det",
    "GB": "gb",
    "HOU": "hou",
    "IND": "ind",
    "JAX": "jax",
    "KC": "kc",
    "JAC": "jax",
    "LA": "lar",
    "LAR": "lar",
    "LAC": "lac",
    "LV": "lv",
    "MIA": "mia",
    "MIN": "min",
    "NE": "ne",
    "NO": "no",
    "NYG": "nyg",
    "NYJ": "nyj",
    "PHI": "phi",
    "PIT": "pit",
    "SEA": "sea",
    "SF": "sf",
    "TB": "tb",
    "TEN": "ten",
    "WAS": "wsh",
    "WSH": "wsh",
    "WFT": "wft",
    "SD": "sd",
    "STL": "stl",
    "OAK": "oak",
}

TEAM_COLORS = {
    "ARI": "#97233F",
    "ATL": "#A71930",
    "BAL": "#241773",
    "BUF": "#00338D",
    "CAR": "#0085CA",
    "CHI": "#00143F",
    "CIN": "#FB4F14",
    "CLE": "#FB4F14",
    "DAL": "#B0B7BC",
    "DEN": "#002244",
    "DET": "#046EB4",
    "GB": "#24423C",
    "HOU": "#C9243F",
    "IND": "#003D79",
    "JAX": "#136677",
    "KC": "#CA2430",
    "LA": "#002147",
    "LAR": "#002147",
    "LAC": "#2072BA",
    "LV": "#C4C9CC",
    "MIA": "#0091A0",
    "MIN": "#4F2E84",
    "NE": "#0A2342",
    "NO": "#A08A58",
    "NYG": "#192E6C",
    "NYJ": "#203731",
    "PHI": "#014A53",
    "PIT": "#FFC20E",
    "SEA": "#7AC142",
    "SF": "#C9243F",
    "TB": "#D40909",
    "TEN": "#4095D1",
    "WAS": "#FFC20F",
}

RANKING_LOGO_SCALE_OVERRIDES = {
    "NYJ": 0.23,
}

TEAM_OPTIONS = [
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
    "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
    "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG",
    "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS",
]

DIVISIONS = {
    "AFC East": {"BUF", "MIA", "NE", "NYJ"},
    "AFC North": {"BAL", "CIN", "CLE", "PIT"},
    "AFC South": {"HOU", "IND", "JAX", "TEN"},
    "AFC West": {"DEN", "KC", "LAC", "LV"},
    "NFC East": {"DAL", "NYG", "PHI", "WAS"},
    "NFC North": {"CHI", "DET", "GB", "MIN"},
    "NFC South": {"ATL", "CAR", "NO", "TB"},
    "NFC West": {"ARI", "LAR", "SEA", "SF"},
}

TEAM_TO_DIVISION = {
    team: division
    for division, teams in DIVISIONS.items()
    for team in teams
}

VIEW_MODES = {
    "Matchup": "matchup",
    "Team Games": "team",
    "Divisional Games": "division",
    "Playoff Games": "playoffs",
    "All Games": "all",
}

APP_PAGES = {
    "Game Explorer": "game_explorer",
    "Team Rankings": "team_rankings",
}

TEAM_ALIASES = {
    "ARI": "ARI",
    "ATL": "ATL",
    "BAL": "BAL",
    "BUF": "BUF",
    "CAR": "CAR",
    "CHI": "CHI",
    "CIN": "CIN",
    "CLE": "CLE",
    "DAL": "DAL",
    "DEN": "DEN",
    "DET": "DET",
    "GB": "GB",
    "HOU": "HOU",
    "IND": "IND",
    "JAC": "JAX",
    "JAX": "JAX",
    "KC": "KC",
    "LA": "LAR",
    "LAR": "LAR",
    "STL": "LAR",
    "LAC": "LAC",
    "SD": "LAC",
    "LV": "LV",
    "OAK": "LV",
    "MIA": "MIA",
    "MIN": "MIN",
    "NE": "NE",
    "NO": "NO",
    "NYG": "NYG",
    "NYJ": "NYJ",
    "PHI": "PHI",
    "PIT": "PIT",
    "SEA": "SEA",
    "SF": "SF",
    "TB": "TB",
    "TEN": "TEN",
    "WAS": "WAS",
    "WSH": "WAS",
    "WFT": "WAS",
}

SEASON_TYPE_LABELS = {
    "REG": "Regular Season",
    "POST": "Playoffs",
    "WC": "Wild Card",
    "DIV": "Divisional",
    "CON": "Conference Championship",
    "SB": "Super Bowl",
}

CURRENT_DATE = datetime.now()
CURRENT_YEAR = CURRENT_DATE.year


def latest_completed_season(today):
    # Before preseason begins, the current NFL season has not produced completed games yet.
    return today.year if today.month >= 8 else today.year - 1


LATEST_COMPLETED_SEASON = latest_completed_season(CURRENT_DATE)
DEFAULT_SEASONS = list(range(LATEST_COMPLETED_SEASON - 4, LATEST_COMPLETED_SEASON + 1))
ALL_GAMES_PAGE_SIZE = 50
FIELD_CHART_FIGSIZE = (16, 5.2)
WP_CHART_FIGSIZE = (16, 4.8)


def to_pandas(df):
    return df.to_pandas() if hasattr(df, "to_pandas") else df


def is_empty_frame(df):
    return len(df.index) == 0


def is_empty_series(series):
    return len(series.index) == 0


def normalize_team_abbr(team):
    return (team or "").strip().upper()


def canonical_team_abbr(team):
    return TEAM_ALIASES.get(normalize_team_abbr(team), normalize_team_abbr(team))


def logo_url(team):
    normalized = normalize_team_abbr(team)
    slug = TEAM_LOGO_SLUGS.get(normalized, normalized.lower())
    return f"https://a.espncdn.com/i/teamlogos/nfl/500/{slug}.png"


def display_team_abbr(team):
    normalized = normalize_team_abbr(team)
    if normalized in TEAM_LOGO_SLUGS:
        return normalized
    return canonical_team_abbr(normalized)


def inject_logo_picker_support():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {
            overflow: visible !important;
        }
        .team-picker {
            position: relative;
            margin-bottom: 0.5rem;
        }
        .team-picker details {
            position: relative;
        }
        .team-picker summary {
            list-style: none;
            cursor: pointer;
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: 0.45rem 0.7rem;
            background: white;
            font-weight: 600;
        }
        .team-picker summary::-webkit-details-marker {
            display: none;
        }
        .team-picker .panel {
            display: none;
            position: fixed;
            width: 260px;
            max-height: 320px;
            overflow-y: auto;
            background: white;
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-radius: 0.75rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.16);
            padding: 0.8rem;
            z-index: 99999;
        }
        .team-picker details[open] .panel {
            display: block;
        }
        .team-picker .grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.7rem 0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_logo_team_picker(state_key, title):
    selected_team = st.session_state.get(state_key)
    selected_label = selected_team if selected_team else "Select team"

    if selected_team:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.35rem;">
                <strong>{title}</strong>
                <img src="{logo_url(selected_team)}" style="width:28px;height:28px;object-fit:contain;" />
                <span style="font-weight:700;">{selected_team}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"**{title}**")

    tiles_html = "".join(
        f"""<a href="{team_picker_href(state_key, team)}" target="_self"
           style="text-decoration:none;color:inherit;text-align:center;display:block;">
            <img src="{logo_url(team)}"
                 style="width:54px;height:54px;object-fit:contain;display:block;margin:0 auto;" />
        </a>"""
        for team in TEAM_OPTIONS
    )

    st.markdown(
        f"""<div class="team-picker {state_key}-picker">
            <details>
                <summary>{selected_label}</summary>
                <div class="panel"><div class="grid">{tiles_html}</div></div>
            </details>
        </div>""",
        unsafe_allow_html=True,
    )

    return st.session_state.get(state_key)


def sync_ui_state_from_query():
    app_page_label = st.query_params.get("app_page")
    if app_page_label in APP_PAGES and "app_page_label" not in st.session_state:
        st.session_state["app_page_label"] = app_page_label

    view_label = st.query_params.get("view")
    if view_label in VIEW_MODES and "view_mode_label" not in st.session_state:
        st.session_state["view_mode_label"] = view_label

    for state_key in ("selected_team_1", "selected_team_2"):
        query_value = st.query_params.get(state_key)
        if query_value in TEAM_OPTIONS and state_key not in st.session_state:
            st.session_state[state_key] = query_value

    start_value = st.query_params.get("season_start")
    end_value = st.query_params.get("season_end")
    if start_value and end_value and "season_range" not in st.session_state:
        try:
            start_year = max(2006, min(int(start_value), LATEST_COMPLETED_SEASON))
            end_year = max(2006, min(int(end_value), LATEST_COMPLETED_SEASON))
            if start_year > end_year:
                start_year, end_year = end_year, start_year
            st.session_state["season_range"] = (start_year, end_year)
        except ValueError:
            pass

    page_value = st.query_params.get("page")
    if page_value and "all_games_page" not in st.session_state:
        try:
            st.session_state["all_games_page"] = max(1, int(page_value))
        except ValueError:
            pass


def team_picker_href(state_key, team):
    params = {}
    app_page_label = st.session_state.get("app_page_label")
    if app_page_label:
        params["app_page"] = app_page_label
    view_label = st.session_state.get("view_mode_label")
    if app_page_label == "Game Explorer" and view_label:
        params["view"] = view_label
    keys = ("selected_team_1", "selected_team_2") if view_label == "Matchup" else ("selected_team_1",)
    for key in keys:
        current_value = st.session_state.get(key)
        if current_value:
            params[key] = current_value
    season_range = st.session_state.get("season_range")
    if season_range:
        params["season_start"] = season_range[0]
        params["season_end"] = season_range[1]
    params[state_key] = team
    return f"?{urlencode(params)}"


def sync_query_params_to_state():
    params = {}
    app_page_label = st.session_state.get("app_page_label")
    if app_page_label:
        params["app_page"] = app_page_label

    view_label = st.session_state.get("view_mode_label")
    if app_page_label == "Game Explorer" and view_label:
        params["view"] = view_label

    selected_team_1 = st.session_state.get("selected_team_1")
    selected_team_2 = st.session_state.get("selected_team_2")
    if app_page_label == "Game Explorer" and selected_team_1:
        params["selected_team_1"] = selected_team_1
    if app_page_label == "Game Explorer" and view_label == "Matchup" and selected_team_2:
        params["selected_team_2"] = selected_team_2

    season_range = st.session_state.get("season_range")
    if season_range:
        params["season_start"] = str(season_range[0])
        params["season_end"] = str(season_range[1])
    if app_page_label == "Game Explorer" and view_label == "All Games":
        params["page"] = str(max(1, int(st.session_state.get("all_games_page", 1))))

    current_params = {key: str(value) for key, value in st.query_params.items()}
    target_params = {key: str(value) for key, value in params.items()}
    if current_params != target_params:
        st.query_params.clear()
        for key, value in target_params.items():
            st.query_params[key] = value


def detect_schedule_loader():
    if nfl is None:
        return None

    for loader_name in ("load_schedules", "load_schedule", "load_games"):
        loader = getattr(nfl, loader_name, None)
        if loader is not None:
            return loader
    return None


@st.cache_data(show_spinner=False)
def load_schedule_data(seasons):
    if nfl is None:
        return pd.DataFrame(), "The `nflreadpy` package is not installed in this environment."

    loader = detect_schedule_loader()
    if loader is None:
        return pd.DataFrame(), "No schedule loader was found in `nflreadpy`."

    last_error = None
    for attempt in range(3):
        try:
            try:
                df = loader(seasons=seasons)
            except TypeError:
                try:
                    df = loader(seasons)
                except TypeError:
                    frames = []
                    for season in seasons:
                        frames.append(to_pandas(loader(season)))
                    df = pd.concat(frames, ignore_index=True)

            return to_pandas(df), None
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))

    return pd.DataFrame(), str(last_error)


@st.cache_data(show_spinner=False)
def load_pbp_data(seasons):
    if nfl is None:
        return pd.DataFrame(), "The `nflreadpy` package is not installed in this environment."

    last_error = None
    for attempt in range(3):
        try:
            try:
                df = nfl.load_pbp(seasons=seasons)
            except TypeError:
                frames = []
                for season in seasons:
                    frames.append(to_pandas(nfl.load_pbp(seasons=[season])))
                df = pd.concat(frames, ignore_index=True)

            return to_pandas(df), None
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))

    # Final fallback: try each season independently so one transient fetch failure
    # does not block the whole request.
    frames = []
    for season in seasons:
        season_error = None
        for attempt in range(3):
            try:
                frames.append(to_pandas(nfl.load_pbp(seasons=[season])))
                season_error = None
                break
            except Exception as exc:
                season_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        if season_error is not None:
            last_error = season_error
            return pd.DataFrame(), str(last_error)

    if frames:
        return pd.concat(frames, ignore_index=True), None

    return pd.DataFrame(), str(last_error)


def first_existing(df, candidates, default=None):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return default


def prepare_game_catalog(schedule_df, view_mode, team1=None, team2=None):
    if schedule_df.empty:
        return pd.DataFrame()

    home_col = first_existing(schedule_df, ["home_team", "home"])
    away_col = first_existing(schedule_df, ["away_team", "away"])
    game_id_col = first_existing(schedule_df, ["game_id"])
    season_col = first_existing(schedule_df, ["season"])
    week_col = first_existing(schedule_df, ["week"])
    home_score_col = first_existing(schedule_df, ["home_score"])
    away_score_col = first_existing(schedule_df, ["away_score"])
    game_type_col = first_existing(schedule_df, ["game_type", "season_type", "game_type_abbr"])
    gameday_col = first_existing(schedule_df, ["gameday", "game_date", "date"])
    overtime_col = first_existing(schedule_df, ["overtime", "ot", "over_time", "is_overtime"])
    total_qtrs_col = first_existing(schedule_df, ["total_qtrs", "total_quarters", "qtrs", "quarters"])

    required_cols = [home_col, away_col, game_id_col, season_col, week_col]
    if any(col is None for col in required_cols):
        return pd.DataFrame()

    games = schedule_df.copy()
    games["display_home_team"] = games[home_col].astype(str).map(display_team_abbr)
    games["display_away_team"] = games[away_col].astype(str).map(display_team_abbr)
    games[home_col] = games[home_col].astype(str).map(canonical_team_abbr)
    games[away_col] = games[away_col].astype(str).map(canonical_team_abbr)

    if home_score_col and away_score_col:
        games = games[games[home_score_col].notna() & games[away_score_col].notna()].copy()

    if games.empty:
        return pd.DataFrame()

    games["season"] = pd.to_numeric(games[season_col], errors="coerce")
    games["week"] = pd.to_numeric(games[week_col], errors="coerce")
    games["home_team"] = games[home_col].map(canonical_team_abbr)
    games["away_team"] = games[away_col].map(canonical_team_abbr)
    games["game_id"] = games[game_id_col]
    games["home_score"] = pd.to_numeric(games[home_score_col], errors="coerce") if home_score_col else None
    games["away_score"] = pd.to_numeric(games[away_score_col], errors="coerce") if away_score_col else None
    games["game_type"] = games[game_type_col].astype(str).str.upper() if game_type_col else "REG"
    games["is_playoff"] = games["game_type"].ne("REG")
    games["division_home"] = games["home_team"].map(TEAM_TO_DIVISION)
    games["division_away"] = games["away_team"].map(TEAM_TO_DIVISION)
    games["went_ot"] = False

    if overtime_col:
        overtime_values = games[overtime_col]
        if pd.api.types.is_bool_dtype(overtime_values):
            games["went_ot"] = overtime_values.fillna(False)
        elif pd.api.types.is_numeric_dtype(overtime_values):
            games["went_ot"] = pd.to_numeric(overtime_values, errors="coerce").fillna(0).gt(0)
        else:
            normalized_ot = overtime_values.astype(str).str.strip().str.upper()
            games["went_ot"] = normalized_ot.isin({"TRUE", "T", "YES", "Y", "1", "OT"})
    elif total_qtrs_col:
        games["went_ot"] = pd.to_numeric(games[total_qtrs_col], errors="coerce").fillna(4).gt(4)

    if view_mode == "matchup":
        if not team1 or not team2:
            return pd.DataFrame()
        matchup_mask = (
            ((games["home_team"] == team1) & (games["away_team"] == team2))
            | ((games["home_team"] == team2) & (games["away_team"] == team1))
        )
        games = games[matchup_mask].copy()
    elif view_mode == "team":
        if not team1:
            return pd.DataFrame()
        games = games[(games["home_team"] == team1) | (games["away_team"] == team1)].copy()
    elif view_mode == "division":
        games = games[
            games["division_home"].notna()
            & games["division_home"].eq(games["division_away"])
        ].copy()
        if team1:
            games = games[(games["home_team"] == team1) | (games["away_team"] == team1)].copy()
    elif view_mode == "playoffs":
        games = games[games["is_playoff"]].copy()
        if team1:
            games = games[(games["home_team"] == team1) | (games["away_team"] == team1)].copy()
    elif view_mode == "all":
        games = games.copy()
    else:
        return pd.DataFrame()

    if games.empty:
        return pd.DataFrame()

    if gameday_col:
        games["gameday"] = pd.to_datetime(games[gameday_col], errors="coerce")
    else:
        games["gameday"] = pd.NaT

    games = games.sort_values(
        by=["season", "gameday", "week"],
        ascending=[False, False, False],
        na_position="last",
    ).reset_index(drop=True)

    return games[
        [
            "game_id",
            "season",
            "week",
            "gameday",
            "game_type",
            "is_playoff",
            "home_team",
            "away_team",
            "display_home_team",
            "display_away_team",
            "home_score",
            "away_score",
            "went_ot",
            "division_home",
            "division_away",
        ]
    ]


def build_drive_summary(game_df):
    needed_cols = [
        "drive",
        "posteam",
        "qtr",
        "time",
        "play_type",
        "yardline_100",
        "drive_end_transition",
    ]
    available_cols = [col for col in needed_cols if col in game_df.columns]
    game_df = game_df.loc[:, available_cols].copy()

    if "play_type" in game_df.columns:
        game_df = game_df[~game_df["play_type"].isin(["kickoff", "extra_point"])].copy()

    if game_df.empty:
        return pd.DataFrame()

    if "qtr" in game_df.columns:
        game_df["qtr"] = pd.to_numeric(game_df["qtr"], errors="coerce")
    if "posteam" in game_df.columns:
        game_df["posteam"] = game_df["posteam"].astype(str).map(canonical_team_abbr)

    game_df = game_df.sort_values(by=["qtr", "time"], ascending=[True, False]).reset_index(drop=True)

    drive_start = game_df.groupby("drive", as_index=False).first()
    drive_end = game_df.groupby("drive", as_index=False).last()
    drive = pd.merge(drive_start, drive_end, on="drive", suffixes=("_start", "_end"))

    drive = drive.rename(
        columns={
            "qtr_start": "qtr",
            "posteam_start": "posteam",
            "yardline_100_start": "yardline_start",
            "yardline_100_end": "yardline_end",
            "drive_end_transition_end": "drive_result",
        }
    )

    drive_cols = [
        "drive",
        "posteam",
        "qtr",
        "yardline_start",
        "yardline_end",
        "drive_result",
    ]
    drive_final = drive[[col for col in drive_cols if col in drive.columns]].copy()

    if "drive_result" in drive_final.columns:
        touchdown_mask = drive_final["drive_result"].astype(str).str.upper().eq("TOUCHDOWN")
        drive_final.loc[touchdown_mask, "yardline_end"] = 0

    drive_final["yardline_start"] = pd.to_numeric(drive_final["yardline_start"], errors="coerce")
    drive_final["yardline_end"] = pd.to_numeric(drive_final["yardline_end"], errors="coerce")
    drive_final["qtr"] = pd.to_numeric(drive_final["qtr"], errors="coerce")
    drive_final = drive_final.dropna(subset=["posteam", "yardline_start", "yardline_end", "qtr"]).reset_index(drop=True)

    return drive_final


def render_matchup_card(row, idx):
    display_away_team = row.get("display_away_team", row["away_team"])
    display_home_team = row.get("display_home_team", row["home_team"])
    final_label = "Final OT" if bool(row.get("went_ot", False)) else "Final"
    with st.container(border=True):
        left, middle, right = st.columns([1.7, 4.3, 1.8])

        with left:
            logo_cols = st.columns([1, 0.35, 1])
            with logo_cols[0]:
                st.image(logo_url(display_away_team), width=64)
                st.caption(display_away_team)
            with logo_cols[1]:
                st.markdown("<div style='text-align:center;padding-top:24px;'>vs</div>", unsafe_allow_html=True)
            with logo_cols[2]:
                st.image(logo_url(display_home_team), width=64)
                st.caption(display_home_team)

        with middle:
            season_type = SEASON_TYPE_LABELS.get(row["game_type"], row["game_type"])
            gameday = row["gameday"].strftime("%b %d, %Y") if pd.notna(row["gameday"]) else "Date unavailable"
            st.markdown(
                f"""
                **Week {int(row['week']) if pd.notna(row['week']) else '?'} • {int(row['season']) if pd.notna(row['season']) else '?'}**  
                {season_type}  
                {gameday}
                """
            )

        with right:
            st.markdown(
                f"""
                    <div style="text-align:right;">
                    <div style="font-size:0.9rem;color:#666;">{final_label}</div>
                    <div style="font-size:1.3rem;font-weight:700;">
                        {int(row['away_score'])} - {int(row['home_score'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Explore", key=f"visualize_{idx}", width="stretch"):
                st.session_state["selected_game_id"] = row["game_id"]
                st.session_state["show_game_dialog"] = True


def drive_side_x(yardline_value, offense_team, quarter_value, team1):
    if int(quarter_value) % 2 != 0:
        return yardline_value if offense_team == team1 else 100 - yardline_value
    return 100 - yardline_value if offense_team == team1 else yardline_value


def drive_bar_geometry(row, team1):
    ystart = float(row["yardline_start"])
    yend = float(row["yardline_end"])
    qmod = int(row["qtr"]) % 2
    posteam = row["posteam"]

    if qmod != 0:
        if posteam == team1:
            left = ystart
            width = yend - ystart
        else:
            left = 100 - ystart
            width = ystart - yend
    else:
        if posteam == team1:
            left = 100 - ystart
            width = ystart - yend
        else:
            left = ystart
            width = yend - ystart

    start_x = left
    end_x = left + width

    return {
        "left": left,
        "width": width,
        "start_x": start_x,
        "end_x": end_x,
    }


def chart_layout(drive_count):
    row_spacing = 4.0
    bar_height = 3.5
    half_bar = bar_height / 2
    row_centers = [i * row_spacing for i in range(drive_count)]
    field_padding_y = 0.6
    field_ymin = -half_bar - field_padding_y
    field_ymax = (row_centers[-1] + half_bar + field_padding_y) if row_centers else 8.0
    field_length = 100.0
    return {
        "row_spacing": row_spacing,
        "bar_height": bar_height,
        "half_bar": half_bar,
        "field_padding_y": field_padding_y,
        "row_centers": row_centers,
        "field_ymin": field_ymin,
        "field_ymax": field_ymax,
        "field_length": field_length,
    }


def add_quarter_background(ax, drive_final, layout):
    quarter_colors = ["#d8ead1", "#c8e0bc", "#b3d49d", "#95c178", "#74ab57"]
    quarter_rows = drive_final.groupby("qtr").agg(first_row=("row_idx", "min"), last_row=("row_idx", "max")).reset_index()

    ax.add_patch(
        patches.Rectangle(
            (0, layout["field_ymin"]),
            layout["field_length"],
            layout["field_ymax"] - layout["field_ymin"],
            facecolor=quarter_colors[0],
            edgecolor="none",
            linewidth=0,
            zorder=0,
        )
    )

    if quarter_rows.empty:
        return quarter_colors[:1]

    limit = min(len(quarter_rows), len(quarter_colors))
    for idx in range(limit):
        first_center = layout["row_centers"][int(quarter_rows.iloc[idx]["first_row"])]
        last_center = layout["row_centers"][int(quarter_rows.iloc[idx]["last_row"])]
        y0 = first_center - layout["half_bar"] - layout["field_padding_y"]
        y1 = last_center + layout["half_bar"] + layout["field_padding_y"]
        if idx == 0:
            y0 = layout["field_ymin"]
        if idx == limit - 1:
            y1 = layout["field_ymax"]
        ax.add_patch(
            patches.Rectangle(
                (0, y0),
                layout["field_length"],
                y1 - y0,
                facecolor=quarter_colors[idx],
                edgecolor="none",
                linewidth=0,
                zorder=1,
            )
        )
    return quarter_colors[:limit]


def get_quarter_colors(drive_final):
    quarter_colors = ["#d8ead1", "#c8e0bc", "#b3d49d", "#95c178", "#74ab57"]
    if drive_final.empty or "qtr" not in drive_final.columns:
        return quarter_colors[:1]
    quarter_count = min(drive_final["qtr"].dropna().nunique(), len(quarter_colors))
    return quarter_colors[: max(quarter_count, 1)]


def add_drive_markers(ax, drive_final, team1, layout):
    cap_width = 0.6
    result_colors = {
        "TOUCHDOWN": "orange",
        "FIELD_GOAL": "gold",
        "PUNT": "brown",
        "INTERCEPTION": "blue",
        "FUMBLE": "blue",
        "DOWNS": "purple",
    }

    for i, row in drive_final.iterrows():
        bottom = layout["row_centers"][i] - (layout["bar_height"] / 2)
        geometry = drive_bar_geometry(row, team1)
        start_x = geometry["start_x"] if geometry["width"] >= 0 else geometry["start_x"] - cap_width
        ax.add_patch(
            patches.Rectangle(
                (start_x, bottom),
                cap_width,
                layout["bar_height"],
                facecolor="0.95",
                edgecolor="0.95",
                linewidth=0.4,
                zorder=20,
            )
        )

        result = str(row.get("drive_result", "")).upper()
        if result not in result_colors:
            continue
        if geometry["width"] >= 0:
            result_x = geometry["end_x"] - cap_width
        else:
            result_x = geometry["end_x"]

        ax.add_patch(
            patches.Rectangle(
                (result_x, bottom),
                cap_width,
                layout["bar_height"],
                facecolor=result_colors[result],
                edgecolor=result_colors[result],
                linewidth=0.4,
                zorder=25,
            )
        )


def add_yard_numbers(ax, layout):
    count = 1
    for yard in range(10, 51, 10):
        ax.text(yard, -6.5, str(count), fontsize=14, color="black", ha="right")
        ax.text(100 - yard, -6.5, str(count), fontsize=14, color="black", ha="right")
        ax.text(yard, 1.0, str(count), transform=ax.get_xaxis_transform(), fontsize=14, color="black", ha="right", va="bottom", clip_on=False)
        ax.text(100 - yard, 1.0, str(count), transform=ax.get_xaxis_transform(), fontsize=14, color="black", ha="right", va="bottom", clip_on=False)
        count += 1

    for yard in range(10, 100, 10):
        ax.text(yard, -6.5, "0", fontsize=14, color="black", ha="left")
        ax.text(yard, 1.0, "0", transform=ax.get_xaxis_transform(), fontsize=14, color="black", ha="left", va="bottom", clip_on=False)


def render_legend_block(title, items):
    swatches = []
    for label, color in items:
        swatches.append(
            f"<span style='display:inline-flex;align-items:center;margin-right:14px;margin-bottom:6px;'>"
            f"<span style='display:inline-block;width:14px;height:14px;background:{color};"
            f"border:1px solid rgba(0,0,0,0.18);margin-right:6px;'></span>{label}</span>"
        )
    st.markdown(
        f"<div style='font-size:0.92rem;'><strong>{title}</strong><br>{''.join(swatches)}</div>",
        unsafe_allow_html=True,
    )


def format_stat_value(value, decimals=1, suffix=""):
    if pd.isna(value):
        return "—"
    if decimals == 0:
        return f"{int(round(float(value)))}{suffix}"
    return f"{float(value):.{decimals}f}{suffix}"


def format_signed_stat_value(value, decimals=2, suffix=""):
    if pd.isna(value):
        return "—"
    return f"{float(value):+.{decimals}f}{suffix}"


def compute_game_stats(game_df, matchup_row):
    teams = [matchup_row["away_team"], matchup_row["home_team"]]
    stats = {
        team: {
            "total_plays": 0,
            "passing_yards": 0.0,
            "rushing_yards": 0.0,
            "pass_epa_per_play": None,
            "rush_epa_per_play": None,
            "pass_success_rate": None,
            "rush_success_rate": None,
            "pass_success_counts": "0/0",
            "rush_success_counts": "0/0",
            "turnovers": 0,
            "sacks_allowed": 0,
            "fourth_down_rate": None,
            "fourth_down_counts": "0/0",
            "explosive_plays": 0,
            "redzone_efficiency": None,
            "redzone_td_trips": "0/0",
        }
        for team in teams
    }

    if is_empty_frame(game_df) or "posteam" not in game_df.columns:
        return stats

    normalized_game_df = game_df.copy()
    normalized_game_df["posteam"] = normalized_game_df["posteam"].astype(str).map(canonical_team_abbr)
    offense_df = normalized_game_df[normalized_game_df["posteam"].isin(teams)].copy()
    if is_empty_frame(offense_df):
        return stats

    play_type_series = (
        offense_df["play_type"].astype(str).str.lower()
        if "play_type" in offense_df.columns
        else pd.Series("", index=offense_df.index, dtype="object")
    )
    offense_df["is_pass"] = play_type_series.eq("pass")
    offense_df["is_rush"] = play_type_series.eq("run")
    offense_df["is_offense_play"] = offense_df["is_pass"] | offense_df["is_rush"]
    offense_df["is_sack"] = play_type_series.eq("sack")
    pass_yards_source = (
        offense_df["passing_yards"]
        if "passing_yards" in offense_df.columns
        else pd.Series(0.0, index=offense_df.index, dtype="float64")
    )
    offense_df["pass_yards_value"] = pd.to_numeric(pass_yards_source, errors="coerce").where(lambda s: s.notna(), 0.0)
    rush_yards_source = (
        offense_df["rushing_yards"]
        if "rushing_yards" in offense_df.columns
        else pd.Series(0.0, index=offense_df.index, dtype="float64")
    )
    offense_df["rush_yards_value"] = pd.to_numeric(rush_yards_source, errors="coerce").where(lambda s: s.notna(), 0.0)
    yards_gained_source = (
        offense_df["yards_gained"]
        if "yards_gained" in offense_df.columns
        else pd.Series(0.0, index=offense_df.index, dtype="float64")
    )
    offense_df["yards_gained_value"] = pd.to_numeric(yards_gained_source, errors="coerce").where(lambda s: s.notna(), 0.0)
    offense_df["down_value"] = pd.to_numeric(
        offense_df["down"] if "down" in offense_df.columns else pd.Series(index=offense_df.index, dtype="float64"),
        errors="coerce",
    )
    interception_source = (
        offense_df["interception"]
        if "interception" in offense_df.columns
        else pd.Series(0.0, index=offense_df.index, dtype="float64")
    )
    offense_df["interception_flag"] = pd.to_numeric(interception_source, errors="coerce").where(lambda s: s.notna(), 0.0)
    fumble_source = (
        offense_df["fumble_lost"]
        if "fumble_lost" in offense_df.columns
        else pd.Series(0.0, index=offense_df.index, dtype="float64")
    )
    offense_df["fumble_lost_flag"] = pd.to_numeric(fumble_source, errors="coerce").where(lambda s: s.notna(), 0.0)
    sack_source = (
        offense_df["sack"]
        if "sack" in offense_df.columns
        else pd.Series(0.0, index=offense_df.index, dtype="float64")
    )
    offense_df["sack_flag"] = pd.to_numeric(sack_source, errors="coerce").where(lambda s: s.notna(), 0.0)

    epa_candidates = offense_df[offense_df["is_offense_play"]].copy()

    for team in teams:
        team_df = offense_df[offense_df["posteam"] == team].copy()
        if is_empty_frame(team_df):
            continue

        team_epa_df = epa_candidates[epa_candidates["posteam"] == team].copy()
        pass_df = team_epa_df[team_epa_df["is_pass"]].copy()
        rush_df = team_epa_df[team_epa_df["is_rush"]].copy()

        stats[team]["total_plays"] = int(len(team_epa_df))
        stats[team]["passing_yards"] = pass_df["pass_yards_value"].sum()
        stats[team]["rushing_yards"] = rush_df["rush_yards_value"].sum()
        stats[team]["turnovers"] = int(team_df["interception_flag"].sum() + team_df["fumble_lost_flag"].sum())
        stats[team]["sacks_allowed"] = int(team_df["sack_flag"].sum() + team_df["is_sack"].sum() - ((team_df["sack_flag"] > 0) & team_df["is_sack"]).sum())
        stats[team]["explosive_plays"] = int(
            pass_df["yards_gained_value"].ge(20).sum() + rush_df["yards_gained_value"].ge(10).sum()
        )

        if not is_empty_frame(team_epa_df) and "epa" in team_epa_df.columns:
            team_epa_df["epa"] = pd.to_numeric(team_epa_df["epa"], errors="coerce")
            pass_df["epa"] = pd.to_numeric(pass_df["epa"], errors="coerce")
            rush_df["epa"] = pd.to_numeric(rush_df["epa"], errors="coerce")
            stats[team]["pass_epa_per_play"] = pass_df["epa"].dropna().mean()
            stats[team]["rush_epa_per_play"] = rush_df["epa"].dropna().mean()

        def extract_success_values(play_df):
            if is_empty_frame(play_df):
                return pd.Series(dtype="float64")
            if "success" in play_df.columns:
                return pd.to_numeric(play_df["success"], errors="coerce").dropna()
            if "epa" in play_df.columns:
                epa_values = pd.to_numeric(play_df["epa"], errors="coerce").dropna()
                return epa_values.gt(0).astype(float)
            return pd.Series(dtype="float64")

        pass_success_values = extract_success_values(pass_df)
        rush_success_values = extract_success_values(rush_df)
        if not is_empty_series(pass_success_values):
            pass_successes = int(pass_success_values.sum())
            pass_total = int(len(pass_success_values))
            stats[team]["pass_success_rate"] = pass_successes / pass_total
            stats[team]["pass_success_counts"] = f"{pass_successes}/{pass_total}"
        if not is_empty_series(rush_success_values):
            rush_successes = int(rush_success_values.sum())
            rush_total = int(len(rush_success_values))
            stats[team]["rush_success_rate"] = rush_successes / rush_total
            stats[team]["rush_success_counts"] = f"{rush_successes}/{rush_total}"

        fourth_down_df = team_epa_df[team_epa_df["down_value"].eq(4)].copy()
        fourth_down_success_values = extract_success_values(fourth_down_df)
        if not is_empty_series(fourth_down_success_values):
            fourth_down_successes = int(fourth_down_success_values.sum())
            fourth_down_total = int(len(fourth_down_success_values))
            stats[team]["fourth_down_rate"] = fourth_down_successes / fourth_down_total
            stats[team]["fourth_down_counts"] = f"{fourth_down_successes}/{fourth_down_total}"

        if "drive" in team_df.columns and "yardline_100" in team_df.columns:
            rz_df = team_df[["drive", "yardline_100"]].copy()
            rz_df["yardline_100"] = pd.to_numeric(rz_df["yardline_100"], errors="coerce")
            redzone_trips = rz_df.groupby("drive")["yardline_100"].min().le(20).sum()

            td_trips = 0
            if redzone_trips > 0:
                drive_results = team_df.groupby("drive").last(numeric_only=False)
                if "drive_end_transition" in drive_results.columns:
                    td_trips = drive_results["drive_end_transition"].astype(str).str.upper().eq("TOUCHDOWN").sum()
                elif "touchdown" in team_df.columns:
                    td_by_drive = team_df.groupby("drive")["touchdown"].max()
                    td_trips = pd.to_numeric(td_by_drive, errors="coerce").fillna(0).gt(0).sum()

            stats[team]["redzone_td_trips"] = f"{int(td_trips)}/{int(redzone_trips)}"
            stats[team]["redzone_efficiency"] = (td_trips / redzone_trips) if redzone_trips else None

    return stats


def render_stats_card(stats, matchup_row):
    away_team = matchup_row["away_team"]
    home_team = matchup_row["home_team"]
    display_away_team = matchup_row.get("display_away_team", away_team)
    display_home_team = matchup_row.get("display_home_team", home_team)
    metric_rows = [
        (
            "Total Plays",
            format_stat_value(stats[away_team]["total_plays"], decimals=0),
            format_stat_value(stats[home_team]["total_plays"], decimals=0),
        ),
        (
            "Passing Yards",
            format_stat_value(stats[away_team]["passing_yards"], decimals=0),
            format_stat_value(stats[home_team]["passing_yards"], decimals=0),
        ),
        (
            "Rushing Yards",
            format_stat_value(stats[away_team]["rushing_yards"], decimals=0),
            format_stat_value(stats[home_team]["rushing_yards"], decimals=0),
        ),
        (
            "Passing EPA / Play",
            format_signed_stat_value(stats[away_team]["pass_epa_per_play"], decimals=2),
            format_signed_stat_value(stats[home_team]["pass_epa_per_play"], decimals=2),
        ),
        (
            "Rushing EPA / Play",
            format_signed_stat_value(stats[away_team]["rush_epa_per_play"], decimals=2),
            format_signed_stat_value(stats[home_team]["rush_epa_per_play"], decimals=2),
        ),
        (
            "Pass Success Rate",
            (
                f"{format_stat_value(stats[away_team]['pass_success_rate'] * 100 if stats[away_team]['pass_success_rate'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[away_team]['pass_success_counts']})"
            ),
            (
                f"{format_stat_value(stats[home_team]['pass_success_rate'] * 100 if stats[home_team]['pass_success_rate'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[home_team]['pass_success_counts']})"
            ),
        ),
        (
            "Rush Success Rate",
            (
                f"{format_stat_value(stats[away_team]['rush_success_rate'] * 100 if stats[away_team]['rush_success_rate'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[away_team]['rush_success_counts']})"
            ),
            (
                f"{format_stat_value(stats[home_team]['rush_success_rate'] * 100 if stats[home_team]['rush_success_rate'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[home_team]['rush_success_counts']})"
            ),
        ),
        (
            "Turnovers",
            format_stat_value(stats[away_team]["turnovers"], decimals=0),
            format_stat_value(stats[home_team]["turnovers"], decimals=0),
        ),
        (
            "Sacks Allowed",
            format_stat_value(stats[away_team]["sacks_allowed"], decimals=0),
            format_stat_value(stats[home_team]["sacks_allowed"], decimals=0),
        ),
        (
            "Fourth Down Rate",
            (
                f"{format_stat_value(stats[away_team]['fourth_down_rate'] * 100 if stats[away_team]['fourth_down_rate'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[away_team]['fourth_down_counts']})"
            ),
            (
                f"{format_stat_value(stats[home_team]['fourth_down_rate'] * 100 if stats[home_team]['fourth_down_rate'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[home_team]['fourth_down_counts']})"
            ),
        ),
        (
            "Explosive Plays (Run 10+, Pass 20+)",
            format_stat_value(stats[away_team]["explosive_plays"], decimals=0),
            format_stat_value(stats[home_team]["explosive_plays"], decimals=0),
        ),
        (
            "Redzone Efficiency",
            (
                f"{format_stat_value(stats[away_team]['redzone_efficiency'] * 100 if stats[away_team]['redzone_efficiency'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[away_team]['redzone_td_trips']})"
            ),
            (
                f"{format_stat_value(stats[home_team]['redzone_efficiency'] * 100 if stats[home_team]['redzone_efficiency'] is not None else None, decimals=1, suffix='%')} "
                f"({stats[home_team]['redzone_td_trips']})"
            ),
        ),
    ]

    rows_html = "".join(
        f"""
        <div style="display:grid;grid-template-columns:minmax(150px, 1fr) minmax(78px, auto) minmax(78px, auto);gap:10px;align-items:center;
                    padding:7px 0;border-top:1px solid rgba(0,0,0,0.08);">
            <div style="font-size:0.92rem;color:#4a4a4a;white-space:nowrap;">{label}</div>
            <div style="font-size:0.98rem;font-weight:700;color:{TEAM_COLORS.get(away_team, '#333')};text-align:center;white-space:nowrap;">{away_value}</div>
            <div style="font-size:0.98rem;font-weight:700;color:{TEAM_COLORS.get(home_team, '#333')};text-align:center;white-space:nowrap;">{home_value}</div>
        </div>
        """
        for label, away_value, home_value in metric_rows
    )

    st.markdown(
        f"""
        <div style="background:#f7f8f2;border:1px solid rgba(0,0,0,0.10);border-radius:18px;
                    padding:14px 16px 10px 16px;box-shadow:0 8px 24px rgba(0,0,0,0.06);min-width:340px;">
                <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center;padding-bottom:8px;">
                <div style="text-align:center;">
                    <img src="{logo_url(display_away_team)}" style="width:58px;height:58px;object-fit:contain;" />
                    <div style="font-weight:700;color:{TEAM_COLORS.get(away_team, '#333')};">{display_away_team}</div>
                </div>
                <div style="font-size:0.95rem;color:#666;font-weight:700;">vs</div>
                <div style="text-align:center;">
                    <img src="{logo_url(display_home_team)}" style="width:58px;height:58px;object-fit:contain;" />
                    <div style="font-weight:700;color:{TEAM_COLORS.get(home_team, '#333')};">{display_home_team}</div>
                </div>
            </div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chart_footer(matchup_row, team1, team2, quarter_colors):
    away_team = matchup_row["away_team"]
    home_team = matchup_row["home_team"]
    away_score = int(matchup_row["away_score"])
    home_score = int(matchup_row["home_score"])

    score_col, matchup_col, quarter_col, result_col = st.columns([1.2, 1.6, 2.0, 2.4])

    with score_col:
        st.markdown(
            f"""
            <div style="padding-top:0;">
                <div style="font-size:0.85rem;color:#555;">Final Score</div>
                <div style="font-size:1.2rem;font-weight:700;line-height:1.1;">
                    <span style="color:{TEAM_COLORS.get(away_team, '#333')};">{away_score}</span>
                    <span style="color:#666;"> - </span>
                    <span style="color:{TEAM_COLORS.get(home_team, '#333')};">{home_score}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with matchup_col:
        render_legend_block(
            "Matchup",
            [
                (team1, TEAM_COLORS.get(team1, "#777777")),
                (team2, TEAM_COLORS.get(team2, "#777777")),
            ],
        )

    with quarter_col:
        quarter_labels = ["1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr", "OT Qtr"]
        render_legend_block(
            "Quarter",
            [(quarter_labels[idx], color) for idx, color in enumerate(quarter_colors)],
        )

    with result_col:
        render_legend_block(
            "Results",
            [
                ("Start", "rgb(242,242,242)"),
                ("Punt", "brown"),
                ("TO", "blue"),
                ("Downs", "purple"),
                ("FG", "gold"),
                ("TD", "orange"),
            ],
        )


def render_field_chart(drive_final, matchup_row, team1, team2):
    drive_final = drive_final.reset_index(drop=True).copy()
    drive_final["row_idx"] = range(len(drive_final))
    tm_colors = [TEAM_COLORS.get(team, "#777777") for team in drive_final["posteam"]]
    layout = chart_layout(len(drive_final))
    fig, ax = plt.subplots(figsize=FIELD_CHART_FIGSIZE)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.975, bottom=0.12)

    ax.set_facecolor("#d8ead1")
    quarter_colors = add_quarter_background(ax, drive_final, layout)

    plt.xlim(0, layout["field_length"])
    plt.ylim(layout["field_ymin"], layout["field_ymax"])

    for i, row in drive_final.iterrows():
        geometry = drive_bar_geometry(row, team1)
        ax.barh(
            layout["row_centers"][i],
            geometry["width"],
            left=geometry["left"],
            height=layout["bar_height"],
            color=tm_colors[i],
            edgecolor="#ffffff",
            linewidth=0.6,
            zorder=10,
        )

    add_drive_markers(ax, drive_final, team1, layout)

    for i in range(11):
        ax.vlines(10 * i, layout["field_ymin"], layout["field_ymax"], color="#1f1f1f", linewidth=1.6, alpha=0.9, zorder=9)

    ax.add_patch(
        patches.Rectangle(
            (0, layout["field_ymin"]),
            layout["field_length"],
            layout["field_ymax"] - layout["field_ymin"],
            fill=False,
            edgecolor="#5b5b5b",
            linewidth=1.0,
            zorder=12,
        )
    )

    add_yard_numbers(ax, layout)

    plt.xticks([])
    plt.yticks([])
    st.pyplot(fig)
    plt.close(fig)
    return quarter_colors


def prepare_wp_data(game_df):
    needed_cols = [
        "game_id",
        "home_team",
        "away_team",
        "posteam",
        "time",
        "drive",
        "fixed_drive",
        "qtr",
        "home_wp",
        "wp",
        "home_score",
        "away_score",
        "drive_end_transition",
    ]
    available_cols = [col for col in needed_cols if col in game_df.columns]
    wp_df = game_df.loc[:, available_cols].copy()
    if is_empty_frame(wp_df) or "home_wp" not in wp_df.columns:
        return pd.DataFrame()

    if "qtr" in wp_df.columns:
        wp_df["qtr"] = pd.to_numeric(wp_df["qtr"], errors="coerce")
    wp_df["home_wp"] = pd.to_numeric(wp_df["home_wp"], errors="coerce") * 100
    wp_df = wp_df.dropna(subset=["qtr", "home_wp"]).copy()
    if is_empty_frame(wp_df):
        return pd.DataFrame()

    wp_df = wp_df.sort_values(by=["qtr", "time"], ascending=[True, False]).reset_index(drop=True)
    wp_df["play_num"] = range(len(wp_df))
    if len(wp_df) > 1:
        wp_df["play_num_scaled"] = wp_df["play_num"] / (len(wp_df) - 1) * 200
    else:
        wp_df["play_num_scaled"] = 100.0
    return wp_df


def render_wp_chart(game_df, matchup_row):
    wp_df = prepare_wp_data(game_df)
    if is_empty_frame(wp_df):
        st.info("Win probability data was not available for this game.")
        return

    play_qtr = wp_df.groupby("qtr", as_index=False).last()
    drive_col = "fixed_drive" if "fixed_drive" in wp_df.columns else ("drive" if "drive" in wp_df.columns else None)
    wp_result = wp_df.groupby(drive_col, as_index=False).last() if drive_col else pd.DataFrame()

    home_team = canonical_team_abbr(matchup_row["home_team"])
    away_team = canonical_team_abbr(matchup_row["away_team"])
    display_home_team = matchup_row.get("display_home_team", matchup_row["home_team"])
    display_away_team = matchup_row.get("display_away_team", matchup_row["away_team"])
    home_col = TEAM_COLORS.get(home_team, "#666666")
    away_col = TEAM_COLORS.get(away_team, "#666666")

    fig, ax = plt.subplots(figsize=WP_CHART_FIGSIZE)
    fig.subplots_adjust(left=0.06, right=0.94, top=0.92, bottom=0.12)

    play_num_values = pd.to_numeric(wp_df["play_num_scaled"], errors="coerce").to_numpy(dtype=float)
    home_wp_values = pd.to_numeric(wp_df["home_wp"], errors="coerce").to_numpy(dtype=float)
    home_wp_above = (home_wp_values >= 50).tolist()
    home_wp_below = (home_wp_values < 50).tolist()

    ax.plot(play_num_values, home_wp_values, color="black", linewidth=1.8, zorder=10)
    ax.fill_between(
        play_num_values,
        home_wp_values,
        50,
        where=home_wp_above,
        color=home_col,
        alpha=0.5,
        interpolate=True,
        zorder=2,
    )
    ax.fill_between(
        play_num_values,
        home_wp_values,
        50,
        where=home_wp_below,
        color=away_col,
        alpha=0.5,
        interpolate=True,
        zorder=2,
    )

    ax.axhline(50, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    for i in range(len(play_qtr) - 1):
        ax.axvline(play_qtr["play_num_scaled"].iloc[i], color="black", linewidth=1)
    ax.axvline(200, color="black", linewidth=1)

    quarter_labels = ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "OT"]
    quarter_starts = [0] + play_qtr["play_num_scaled"].iloc[:-1].tolist()
    quarter_ends = play_qtr["play_num_scaled"].tolist()
    for idx, (start_x, end_x) in enumerate(zip(quarter_starts, quarter_ends)):
        if idx >= len(quarter_labels):
            break
        center_x = (start_x + end_x) / 2
        ax.text(
            center_x,
            95,
            quarter_labels[idx],
            fontsize=13,
            color="black",
            ha="center",
            va="center",
            weight="bold",
            path_effects=[pe.withStroke(linewidth=2, foreground="white")],
        )

    ax.set_ylim(0, 100)
    ax.set_xlim(0, 200)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    for i in range(6):
        y_val = 50 + 10 * i
        ax.text(202.5, y_val, str(y_val), fontsize=12, color="black", ha="center", va="center")
        if i != 0:
            ax.text(202.5, 50 - 10 * i, str(y_val), fontsize=12, color="black", ha="center", va="center")
    ax.text(210, 50, "Win Percentage", fontsize=13, color="black", ha="center", va="center", rotation=90)

    ax.text(
        16,
        89,
        display_home_team,
        fontsize=20,
        color=home_col,
        ha="left",
        va="center",
        fontweight="bold",
        alpha=0.85,
    )
    ax.text(
        16,
        11,
        display_away_team,
        fontsize=20,
        color=away_col,
        ha="left",
        va="center",
        fontweight="bold",
        alpha=0.85,
    )

    st.pyplot(fig)
    plt.close(fig)


@st.cache_data(show_spinner=False)
def fetch_logo_image_bytes(team):
    try:
        with urllib.request.urlopen(logo_url(team), timeout=8) as response:
            return response.read()
    except Exception:
        return None


def build_rankings_dataset(pbp_df, seasons):
    if is_empty_frame(pbp_df):
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

    required_cols = ["posteam", "defteam", "week", "season", "play_type", "epa"]
    if any(col not in pbp_df.columns for col in required_cols):
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

    rankings_df = pbp_df.copy()
    rankings_df["season"] = pd.to_numeric(rankings_df["season"], errors="coerce")
    rankings_df["week"] = pd.to_numeric(rankings_df["week"], errors="coerce")
    rankings_df["epa"] = pd.to_numeric(rankings_df["epa"], errors="coerce")
    rankings_df["posteam"] = rankings_df["posteam"].astype(str).map(canonical_team_abbr)
    rankings_df["defteam"] = rankings_df["defteam"].astype(str).map(canonical_team_abbr)
    rankings_df["play_type"] = rankings_df["play_type"].astype(str).str.lower()
    if "season_type" in rankings_df.columns:
        rankings_df["season_type"] = rankings_df["season_type"].astype(str).str.upper()
        rankings_df = rankings_df[rankings_df["season_type"].eq("REG")].copy()
    elif "game_type" in rankings_df.columns:
        rankings_df["game_type"] = rankings_df["game_type"].astype(str).str.upper()
        rankings_df = rankings_df[rankings_df["game_type"].eq("REG")].copy()
    else:
        rankings_df = rankings_df[rankings_df["week"].le(18)].copy()
    rankings_df = rankings_df[
        rankings_df["play_type"].isin(["pass", "run"])
        & rankings_df["posteam"].isin(TEAM_OPTIONS)
        & rankings_df["defteam"].isin(TEAM_OPTIONS)
        & rankings_df["season"].isin(seasons)
    ].copy()

    if rankings_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

    week_points = (
        rankings_df[["season", "week"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["season", "week"])
        .reset_index(drop=True)
    )
    if week_points.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

    week_points["week_index"] = range(1, len(week_points) + 1)
    week_labels = [
        {
            "season": int(row["season"]),
            "week": int(row["week"]),
            "week_index": int(row["week_index"]),
        }
        for _, row in week_points.iterrows()
    ]

    def summarize(side_col, ascending):
        weekly = (
            rankings_df.groupby([side_col, "season", "week"], as_index=False)
            .agg(total_epa=("epa", "sum"), play_count=("epa", "size"))
        )
        weekly = weekly.rename(columns={side_col: "team"})
        team_week_grid = pd.DataFrame(
            [(team, label["season"], label["week"], label["week_index"]) for team in TEAM_OPTIONS for label in week_labels],
            columns=["team", "season", "week", "week_index"],
        )
        weekly = team_week_grid.merge(
            weekly[["team", "season", "week", "total_epa", "play_count"]],
            on=["team", "season", "week"],
            how="left",
        )
        weekly["total_epa"] = weekly["total_epa"].fillna(0.0)
        weekly["play_count"] = weekly["play_count"].fillna(0.0)
        weekly = weekly.sort_values(["team", "season", "week"]).reset_index(drop=True)

        weekly["cum_epa"] = weekly.groupby("team")["total_epa"].cumsum()
        weekly["cum_plays"] = weekly.groupby("team")["play_count"].cumsum()
        weekly["epa_per_play"] = weekly["total_epa"].div(weekly["play_count"].where(weekly["play_count"].ne(0))).fillna(0.0)
        weekly["cumulative_epa_per_play"] = weekly["cum_epa"].div(weekly["cum_plays"].where(weekly["cum_plays"].ne(0))).fillna(0.0)
        weekly["rank"] = weekly.groupby("week_index")["cumulative_epa_per_play"].rank(
            ascending=ascending,
            method="first",
        )
        return weekly

    offense = summarize("posteam", ascending=False)
    defense = summarize("defteam", ascending=True)
    overall = offense.merge(
        defense[["team", "season", "week", "week_index", "cumulative_epa_per_play"]],
        on=["team", "season", "week", "week_index"],
        how="inner",
        suffixes=("_offense", "_defense"),
    )
    overall["cumulative_epa_per_play"] = (
        overall["cumulative_epa_per_play_offense"] - overall["cumulative_epa_per_play_defense"]
    )
    overall["rank"] = overall.groupby("week_index")["cumulative_epa_per_play"].rank(
        ascending=False,
        method="first",
    )

    return offense, defense, overall, week_labels


def draw_team_ranking_lines(ax, ranking_df):
    for team, team_df in ranking_df.groupby("team", sort=False):
        team_df = team_df.sort_values("week_index")
        ax.plot(
            team_df["week_index"],
            team_df["rank"],
            color=TEAM_COLORS.get(team, "#888888"),
            linewidth=1.35,
            alpha=0.55,
            zorder=2,
        )


def normalize_logo_image(image):
    rgba_image = image.convert("RGBA")
    alpha = rgba_image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox:
        rgba_image = rgba_image.crop(bbox)
    max_side = max(rgba_image.size)
    square_image = Image.new("RGBA", (max_side, max_side), (255, 255, 255, 0))
    offset_x = (max_side - rgba_image.size[0]) // 2
    offset_y = (max_side - rgba_image.size[1]) // 2
    square_image.paste(rgba_image, (offset_x, offset_y), rgba_image)
    return square_image


def draw_logo_ranking_points(ax, ranking_df, logo_zoom, logo_interval=6):
    if ranking_df.empty:
        return

    unique_weeks = sorted(ranking_df["week_index"].dropna().unique().tolist())
    if not unique_weeks:
        return

    target_columns = min(5, len(unique_weeks))
    selected_weeks = []
    if target_columns == 1:
        selected_weeks = [unique_weeks[-1]]
    else:
        for idx in range(target_columns):
            position = round(idx * (len(unique_weeks) - 1) / (target_columns - 1))
            selected_weeks.append(unique_weeks[position])
    selected_weeks = sorted(set(selected_weeks))

    marker_df = ranking_df[ranking_df["week_index"].isin(selected_weeks)].copy()
    for _, row in marker_df.iterrows():
        x = row["week_index"]
        y = row["rank"]
        logo_bytes = fetch_logo_image_bytes(row["team"])
        if logo_bytes:
            try:
                image = normalize_logo_image(Image.open(BytesIO(logo_bytes)))
                team_zoom = logo_zoom * RANKING_LOGO_SCALE_OVERRIDES.get(row["team"], 1.0)
                image_box = OffsetImage(np.asarray(image), zoom=team_zoom)
                annotation = AnnotationBbox(image_box, (x, y), frameon=False, zorder=10)
                ax.add_artist(annotation)
                continue
            except Exception:
                pass
        ax.text(
            x,
            y,
            row["team"],
            ha="center",
            va="center",
            fontsize=max(5.5, min(8.5, logo_zoom * 130)),
            fontweight="bold",
            color=TEAM_COLORS.get(row["team"], "#222"),
            bbox=dict(boxstyle="round,pad=0.22", facecolor="white", edgecolor="none", alpha=0.9),
            zorder=10,
        )


def create_ranking_figure(ranking_df, week_labels, title, subtitle, ascending):
    if ranking_df.empty or not week_labels:
        return None

    week_count = len(week_labels)
    fig_width = max(4.8, min(12.5, 0.14 * week_count + 3.6))
    fig, ax = plt.subplots(figsize=(fig_width, 7.9))
    fig.subplots_adjust(left=0.05, right=0.88, top=0.82, bottom=0.18)

    logo_zoom = max(0.016, min(0.044, 1.6 / max(week_count, 1) * 6))
    draw_team_ranking_lines(ax, ranking_df)
    draw_logo_ranking_points(ax, ranking_df, logo_zoom)

    ax.set_xlim(0.5, week_count + 0.5)
    ax.set_ylim(32.8, 0.2)
    ax.grid(axis="both", color="#d9d9d9", linewidth=0.8, alpha=0.8)

    if week_count <= 18:
        tick_positions = [label["week_index"] for label in week_labels]
        tick_labels = [f"{str(label['season'])[-2:]}-{label['week']}" for label in week_labels]
    else:
        sampled = week_labels[:: max(1, week_count // 8)]
        if sampled[-1]["week_index"] != week_labels[-1]["week_index"]:
            sampled.append(week_labels[-1])
        tick_positions = [label["week_index"] for label in sampled]
        tick_labels = [f"{str(label['season'])[-2:]}-{label['week']}" for label in sampled]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks([])

    season_breaks = []
    previous_season = week_labels[0]["season"]
    for label in week_labels[1:]:
        if label["season"] != previous_season:
            season_breaks.append(label["week_index"] - 0.5)
            previous_season = label["season"]
    for x in season_breaks:
        ax.axvline(x, color="#6e6e6e", linewidth=1.4, linestyle="--", alpha=0.75, zorder=1)

    ax.annotate(
        "",
        xy=(1.055, 0.98),
        xytext=(1.055, 0.02),
        xycoords="axes fraction",
        textcoords="axes fraction",
        arrowprops=dict(arrowstyle="->", color="black", linewidth=1.8),
        annotation_clip=False,
    )
    ax.text(1.09, 0.98, "Best", transform=ax.transAxes, ha="left", va="center", fontsize=7.5, fontweight="bold")
    ax.text(1.09, 0.02, "Worst", transform=ax.transAxes, ha="left", va="center", fontsize=7.5, fontweight="bold")

    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=5)
    ax.text(0.5, 0.985, subtitle, fontsize=7.4, ha="center", transform=ax.transAxes, wrap=True)
    ax.set_xlabel("Season-Week", fontsize=8.5, labelpad=4)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    return fig


def render_team_rankings_page(seasons):
    with st.spinner("Loading play-by-play for team rankings..."):
        pbp_df, pbp_err = load_pbp_data(seasons)

    if is_empty_frame(pbp_df):
        st.error(f"Could not load play-by-play data for {seasons[0]}-{seasons[-1]}. {pbp_err or ''}")
        return

    offense_rankings, defense_rankings, overall_rankings, week_labels = build_rankings_dataset(pbp_df, seasons)
    if offense_rankings.empty or defense_rankings.empty or overall_rankings.empty:
        st.warning("No pass/run play data was available to build team rankings for that range.")
        return

    st.caption(
        f"Showing cumulative EPA per play rankings from {seasons[0]} through {seasons[-1]}. "
        "Offense ranks best-to-worst by higher EPA/play; defense ranks best-to-worst by lower EPA/play allowed."
    )

    chart_specs = [
        (
            offense_rankings,
            "Offense Rankings",
            "Cumulative offensive EPA / play",
            False,
        ),
        (
            defense_rankings,
            "Defense Rankings",
            "Cumulative defensive EPA / play allowed",
            True,
        ),
        (
            overall_rankings,
            "Overall Rankings",
            "Offensive EPA/play minus defensive EPA/play allowed",
            False,
        ),
    ]

    ranking_tabs = st.tabs(["Offense Rankings", "Defense Rankings", "Overall Rankings"])
    for tab, (ranking_df, title, subtitle, ascending) in zip(ranking_tabs, chart_specs):
        with tab:
            fig = create_ranking_figure(ranking_df, week_labels, title, subtitle, ascending)
            if fig is None:
                st.info("Ranking data was not available for this season range.")
            else:
                st.pyplot(fig, width="content")
                plt.close(fig)


def render_page_heading(title_text):
    st.markdown(
        f"""
        <div style="margin-top:-1.25rem;margin-bottom:0.2rem;">
            <h1 style="margin:0;padding:0;font-size:3rem;font-weight:700;line-height:1;">{title_text}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_selected_game_visualization(selected_game, team1, team2):
    selected_season = int(selected_game["season"])
    viz_team1 = team1 if team1 else selected_game["away_team"]
    viz_team2 = team2 if team2 else (
        selected_game["home_team"] if viz_team1 != selected_game["home_team"] else selected_game["away_team"]
    )

    with st.spinner("Loading play-by-play for the selected game..."):
        pbp_df, pbp_err = load_pbp_data([selected_season])

    if is_empty_frame(pbp_df):
        st.error(f"Could not load play-by-play data for {selected_season}. {pbp_err or ''}")
        return

    if "game_id" not in pbp_df.columns:
        st.error("The loaded play-by-play data does not include a `game_id` column.")
        return

    game_df = pbp_df[pbp_df["game_id"] == selected_game["game_id"]].copy()
    if game_df.empty:
        st.error("No play-by-play rows were found for the selected game.")
        return

    drive_final = build_drive_summary(game_df)
    if drive_final.empty:
        st.error("No drive data was available to draw the visualization for this game.")
        return

    game_stats = compute_game_stats(game_df, selected_game)
    quarter_colors = get_quarter_colors(drive_final)

    chart_col, stats_col = st.columns([3.2, 1.8])
    with chart_col:
        render_chart_footer(selected_game, viz_team1, viz_team2, quarter_colors)
        render_field_chart(drive_final, selected_game, viz_team1, viz_team2)
        render_wp_chart(game_df, selected_game)
    with stats_col:
        render_stats_card(game_stats, selected_game)


def open_game_dialog(selected_game, team1, team2):
    season_type = SEASON_TYPE_LABELS.get(selected_game["game_type"], selected_game["game_type"])
    display_away_team = selected_game.get("display_away_team", selected_game["away_team"])
    display_home_team = selected_game.get("display_home_team", selected_game["home_team"])
    title = (
        f"{display_away_team} at {display_home_team} "
        f"• Week {int(selected_game['week'])}, {int(selected_game['season'])} ({season_type})"
    )

    try:
        dialog_decorator = st.dialog(title, width="large")
    except TypeError:
        dialog_decorator = st.dialog(title)

    @dialog_decorator
    def _dialog():
        render_selected_game_visualization(selected_game, team1, team2)

    _dialog()


sync_ui_state_from_query()
inject_logo_picker_support()

if "app_page_label" not in st.session_state:
    st.session_state["app_page_label"] = "Game Explorer"

if "season_range" not in st.session_state:
    st.session_state["season_range"] = (max(2006, LATEST_COMPLETED_SEASON - 4), LATEST_COMPLETED_SEASON)

with st.sidebar:
    selected_app_page_label = st.session_state["app_page_label"]
    next_page_label = "Team Rankings" if selected_app_page_label == "Game Explorer" else "Game Explorer"
    if st.button(f"Switch to {next_page_label}", width="stretch"):
        selected_app_page_label = next_page_label
        st.session_state["app_page_label"] = selected_app_page_label
        st.session_state["show_game_dialog"] = False
        st.rerun()
    selected_app_page = APP_PAGES[selected_app_page_label]
    if selected_app_page == "game_explorer":
        selected_view_label = st.radio("View", list(VIEW_MODES.keys()), key="view_mode_label")
        selected_view_mode = VIEW_MODES[selected_view_label]
        if selected_view_mode == "matchup":
            tm1 = render_logo_team_picker("selected_team_1", "First Team")
            tm2 = render_logo_team_picker("selected_team_2", "Second Team")
        elif selected_view_mode in {"team", "division", "playoffs"}:
            tm1 = render_logo_team_picker("selected_team_1", "Team")
            tm2 = None
        else:
            tm1 = None
            tm2 = None
            st.empty()
    else:
        selected_view_mode = VIEW_MODES.get(st.session_state.get("view_mode_label", "Matchup"), "matchup")
        tm1 = None
        tm2 = None
    season_range = st.slider(
        "Season range",
        min_value=2006,
        max_value=LATEST_COMPLETED_SEASON,
        key="season_range",
    )

sync_query_params_to_state()

if selected_app_page == "team_rankings":
    render_page_heading("NFL Team Rankings")
else:
    render_page_heading("NFL Game Explorer")

start_season, end_season = st.session_state["season_range"]
seasons = list(range(start_season, end_season + 1))

if selected_app_page == "team_rankings":
    render_team_rankings_page(seasons)
    st.stop()

if selected_view_mode == "matchup" and (not tm1 or not tm2):
    st.info("Choose two teams from the logo pickers to load matchup history.")
    st.stop()

if selected_view_mode == "matchup" and tm1 == tm2:
    st.warning("Choose two different teams.")
    st.stop()

if selected_view_mode in {"team", "division", "playoffs"} and not tm1:
    st.info("Choose a team from the logo picker to load games.")
    st.stop()

with st.spinner("Loading matchup history..."):
    schedule_df, schedule_err = load_schedule_data(seasons)

if schedule_df.empty:
    st.error(f"Could not load schedule data for {seasons[0]}-{seasons[-1]}. {schedule_err or ''}")
    st.stop()

matchup_games = prepare_game_catalog(schedule_df, selected_view_mode, tm1, tm2)

if selected_view_mode == "matchup":
    st.caption(f"Showing {tm1} vs {tm2} from {seasons[0]} through {seasons[-1]}.")
elif selected_view_mode == "team":
    st.caption(f"Showing all {tm1} games from {seasons[0]} through {seasons[-1]}.")
elif selected_view_mode == "division":
    st.caption(f"Showing all divisional games from {seasons[0]} through {seasons[-1]}.")
elif selected_view_mode == "playoffs":
    st.caption(f"Showing all playoff games from {seasons[0]} through {seasons[-1]}.")
else:
    st.caption(f"Showing all completed games from {seasons[0]} through {seasons[-1]}.")

if matchup_games.empty:
    st.warning("No completed games were found for the selected view in that range.")
    st.stop()

games_to_render = matchup_games
if selected_view_mode == "all":
    total_games = len(matchup_games)
    total_pages = max(1, (total_games + ALL_GAMES_PAGE_SIZE - 1) // ALL_GAMES_PAGE_SIZE)
    current_page = max(1, min(st.session_state.get("all_games_page", 1), total_pages))
    st.session_state["all_games_page"] = current_page

    prev_col, status_col, next_col = st.columns([1, 3, 1])
    with prev_col:
        if st.button("Previous", width="stretch", disabled=current_page == 1):
            st.session_state["all_games_page"] = current_page - 1
            st.rerun()
    with status_col:
        start_idx = (current_page - 1) * ALL_GAMES_PAGE_SIZE + 1
        end_idx = min(current_page * ALL_GAMES_PAGE_SIZE, total_games)
        st.markdown(
            f"<div style='text-align:center;padding-top:0.45rem;'>Showing games {start_idx}-{end_idx} of {total_games} • Page {current_page} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with next_col:
        if st.button("Next", width="stretch", disabled=current_page == total_pages):
            st.session_state["all_games_page"] = current_page + 1
            st.rerun()

    page_start = (current_page - 1) * ALL_GAMES_PAGE_SIZE
    page_end = page_start + ALL_GAMES_PAGE_SIZE
    games_to_render = matchup_games.iloc[page_start:page_end].reset_index(drop=True)
else:
    st.session_state["all_games_page"] = 1

if "selected_game_id" not in st.session_state or st.session_state["selected_game_id"] not in set(matchup_games["game_id"]):
    st.session_state["selected_game_id"] = matchup_games.iloc[0]["game_id"]

if "show_game_dialog" not in st.session_state:
    st.session_state["show_game_dialog"] = False

for row_start in range(0, len(games_to_render), 2):
    cols = st.columns(2)
    row_slice = games_to_render.iloc[row_start:row_start + 2]
    for col_idx, (_, row) in enumerate(row_slice.iterrows()):
        with cols[col_idx]:
            render_matchup_card(row, row_start + col_idx)

selected_game_id = st.session_state["selected_game_id"]
selected_game = matchup_games[matchup_games["game_id"] == selected_game_id]

if selected_game.empty:
    st.warning("Select a game to display the visualization.")
    st.stop()

selected_game = selected_game.iloc[0]

if st.session_state.get("show_game_dialog"):
    if hasattr(st, "dialog"):
        open_game_dialog(selected_game, tm1, tm2)
    else:
        st.info("This Streamlit version does not support popup dialogs, so the visualization is shown inline instead.")
        st.subheader("Selected Game Visualization")
        render_selected_game_visualization(selected_game, tm1, tm2)
    st.session_state["show_game_dialog"] = False
