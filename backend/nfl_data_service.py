from __future__ import annotations

import time
from datetime import datetime
from functools import lru_cache
from typing import Any, Optional

import pandas as pd

try:
    import nflreadpy as nflread
except ImportError:
    nflread = None


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

TEAM_OPTIONS = [
    "ARI",
    "ATL",
    "BAL",
    "BUF",
    "CAR",
    "CHI",
    "CIN",
    "CLE",
    "DAL",
    "DEN",
    "DET",
    "GB",
    "HOU",
    "IND",
    "JAX",
    "KC",
    "LAC",
    "LAR",
    "LV",
    "MIA",
    "MIN",
    "NE",
    "NO",
    "NYG",
    "NYJ",
    "PHI",
    "PIT",
    "SEA",
    "SF",
    "TB",
    "TEN",
    "WAS",
]

TEAM_NAMES = {
    "ARI": "Cardinals",
    "ATL": "Falcons",
    "BAL": "Ravens",
    "BUF": "Bills",
    "CAR": "Panthers",
    "CHI": "Bears",
    "CIN": "Bengals",
    "CLE": "Browns",
    "DAL": "Cowboys",
    "DEN": "Broncos",
    "DET": "Lions",
    "GB": "Packers",
    "HOU": "Texans",
    "IND": "Colts",
    "JAX": "Jaguars",
    "KC": "Chiefs",
    "LAC": "Chargers",
    "LAR": "Rams",
    "LV": "Raiders",
    "MIA": "Dolphins",
    "MIN": "Vikings",
    "NE": "Patriots",
    "NO": "Saints",
    "NYG": "Giants",
    "NYJ": "Jets",
    "PHI": "Eagles",
    "PIT": "Steelers",
    "SEA": "Seahawks",
    "SF": "49ers",
    "TB": "Buccaneers",
    "TEN": "Titans",
    "WAS": "Commanders",
}

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
    "All Games": "all_games",
    "Primetime Games": "all_primetime",
    "Playoff Games": "all_playoffs",
    "Team Games": "team_games",
    "Team Primetime Games": "team_primetime",
    "Team Playoff Games": "team_playoffs",
    "Team Divisional Games": "team_divisional",
    "Divisional Games": "divisional_games",
    "Matchups": "matchup",
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

MIN_SEASON = 2006
MAX_RANKINGS_SEASON = 2025
ALL_GAMES_PAGE_SIZE = 50
PAGINATED_VIEW_MODES = {"all_games", "all_primetime", "all_playoffs", "team_games"}
QUARTER_COLORS = ["#eef8de", "#cdeca0", "#8fd157", "#4f9f3e", "#1f5f31"]


def latest_completed_season(today: datetime) -> int:
    return today.year if today.month >= 8 else today.year - 1


CURRENT_DATE = datetime.now()
LATEST_COMPLETED_SEASON = latest_completed_season(CURRENT_DATE)


def normalize_team_abbr(team: Optional[str]) -> str:
    return (team or "").strip().upper()


def canonical_team_abbr(team: Optional[str]) -> str:
    normalized = normalize_team_abbr(team)
    return TEAM_ALIASES.get(normalized, normalized)


def display_team_abbr(team: Optional[str]) -> str:
    normalized = normalize_team_abbr(team)
    if normalized in TEAM_LOGO_SLUGS:
        return normalized
    return canonical_team_abbr(normalized)


def logo_url(team: Optional[str]) -> str:
    normalized = normalize_team_abbr(team)
    slug = TEAM_LOGO_SLUGS.get(normalized, normalized.lower())
    return f"https://a.espncdn.com/i/teamlogos/nfl/500/{slug}.png"


def default_season_range() -> tuple[int, int]:
    default_start = min(max(MIN_SEASON, 2024), LATEST_COMPLETED_SEASON)
    default_end = min(max(default_start, 2025), LATEST_COMPLETED_SEASON)
    return default_start, default_end


def to_pandas(df: Any) -> pd.DataFrame:
    return df.to_pandas() if hasattr(df, "to_pandas") else df


def is_empty_frame(df: pd.DataFrame) -> bool:
    return len(df.index) == 0


def is_empty_series(series: pd.Series) -> bool:
    return len(series.index) == 0


def first_existing(df: pd.DataFrame, candidates: list[str], default: Optional[str] = None) -> Optional[str]:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return default


def detect_schedule_loader():
    if nflread is None:
        return None
    for loader_name in ("load_schedules", "load_schedule", "load_games"):
        loader = getattr(nflread, loader_name, None)
        if loader is not None:
            return loader
    return None


@lru_cache(maxsize=16)
def load_schedule_data(seasons_key: tuple[int, ...]) -> tuple[pd.DataFrame, Optional[str]]:
    seasons = list(seasons_key)
    if nflread is None:
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
        except Exception as exc:  # pragma: no cover - depends on live data source
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))

    return pd.DataFrame(), str(last_error)


@lru_cache(maxsize=16)
def load_pbp_data(seasons_key: tuple[int, ...]) -> tuple[pd.DataFrame, Optional[str]]:
    seasons = list(seasons_key)
    if nflread is None:
        return pd.DataFrame(), "The `nflreadpy` package is not installed in this environment."

    last_error = None
    for attempt in range(3):
        try:
            try:
                df = nflread.load_pbp(seasons=seasons)
            except TypeError:
                frames = []
                for season in seasons:
                    frames.append(to_pandas(nflread.load_pbp(seasons=[season])))
                df = pd.concat(frames, ignore_index=True)

            return to_pandas(df), None
        except Exception as exc:  # pragma: no cover - depends on live data source
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))

    frames = []
    for season in seasons:
        season_error = None
        for attempt in range(3):
            try:
                frames.append(to_pandas(nflread.load_pbp(seasons=[season])))
                season_error = None
                break
            except Exception as exc:  # pragma: no cover - depends on live data source
                season_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        if season_error is not None:
            last_error = season_error
            return pd.DataFrame(), str(last_error)

    if frames:
        return pd.concat(frames, ignore_index=True), None

    return pd.DataFrame(), str(last_error)


def detect_primetime_games(games: pd.DataFrame) -> pd.Series:
    weekday_col = first_existing(games, ["weekday", "game_day", "day"])
    gametime_col = first_existing(games, ["gametime", "game_time", "start_time", "start_time_eastern"])

    if weekday_col:
        weekday_values = games[weekday_col].astype(str).str.strip().str.upper()
    else:
        weekday_values = pd.Series("", index=games.index, dtype="object")

    if gametime_col:
        gametime_values = games[gametime_col].astype(str).str.strip().str.upper()
    else:
        gametime_values = pd.Series("", index=games.index, dtype="object")

    sunday_mask = weekday_values.isin({"SUN", "SUNDAY"})
    sunday_regular_window = gametime_values.str.contains(
        (
            r"(?:"
            r"1:00(?:\s*PM)?|1:05(?:\s*PM)?|1:25(?:\s*PM)?|"
            r"4:05(?:\s*PM)?|4:25(?:\s*PM)?|"
            r"10:00(?:\s*AM)?|10:05(?:\s*AM)?|10:25(?:\s*AM)?|"
            r"13:00|13:05|13:25|16:05|16:25"
            r")"
        ),
        regex=True,
        na=False,
    )

    return ~(sunday_mask & sunday_regular_window)


def prepare_game_catalog(
    schedule_df: pd.DataFrame,
    view_mode: str,
    team1: Optional[str] = None,
    team2: Optional[str] = None,
) -> pd.DataFrame:
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
    games["is_divisional"] = games["division_home"].notna() & games["division_home"].eq(games["division_away"])
    games["is_primetime"] = detect_primetime_games(games)
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
    elif view_mode == "team_games":
        if not team1:
            return pd.DataFrame()
        games = games[(games["home_team"] == team1) | (games["away_team"] == team1)].copy()
    elif view_mode == "team_primetime":
        if not team1:
            return pd.DataFrame()
        games = games[
            ((games["home_team"] == team1) | (games["away_team"] == team1))
            & games["is_primetime"]
            & ~games["is_playoff"]
        ].copy()
    elif view_mode == "team_playoffs":
        games = games[games["is_playoff"]].copy()
        if not team1:
            return pd.DataFrame()
        games = games[(games["home_team"] == team1) | (games["away_team"] == team1)].copy()
    elif view_mode == "team_divisional":
        if not team1:
            return pd.DataFrame()
        games = games[
            games["is_divisional"]
            & ((games["home_team"] == team1) | (games["away_team"] == team1))
        ].copy()
    elif view_mode == "divisional_games":
        games = games[games["is_divisional"]].copy()
    elif view_mode == "all_playoffs":
        games = games[games["is_playoff"]].copy()
    elif view_mode == "all_primetime":
        games = games[games["is_primetime"] & ~games["is_playoff"]].copy()
    elif view_mode == "all_games":
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


def build_drive_summary(game_df: pd.DataFrame) -> pd.DataFrame:
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


def format_stat_value(value: Any, decimals: int = 1, suffix: str = "") -> str:
    if pd.isna(value):
        return "—"
    if decimals == 0:
        return f"{int(round(float(value)))}{suffix}"
    return f"{float(value):.{decimals}f}{suffix}"


def format_signed_stat_value(value: Any, decimals: int = 2, suffix: str = "") -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):+.{decimals}f}{suffix}"


def compute_game_stats(game_df: pd.DataFrame, matchup_row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    teams = [matchup_row["awayTeam"], matchup_row["homeTeam"]]
    stats = {
        team: {
            "totalPlays": 0,
            "passingYards": 0.0,
            "rushingYards": 0.0,
            "passEpaPerPlay": None,
            "rushEpaPerPlay": None,
            "passSuccessRate": None,
            "rushSuccessRate": None,
            "passSuccessCounts": "0/0",
            "rushSuccessCounts": "0/0",
            "turnovers": 0,
            "sacksAllowed": 0,
            "fourthDownRate": None,
            "fourthDownCounts": "0/0",
            "explosivePlays": 0,
            "redzoneEfficiency": None,
            "redzoneTdTrips": "0/0",
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

        stats[team]["totalPlays"] = int(len(team_epa_df))
        stats[team]["passingYards"] = pass_df["pass_yards_value"].sum()
        stats[team]["rushingYards"] = rush_df["rush_yards_value"].sum()
        stats[team]["turnovers"] = int(team_df["interception_flag"].sum() + team_df["fumble_lost_flag"].sum())
        stats[team]["sacksAllowed"] = int(
            team_df["sack_flag"].sum() + team_df["is_sack"].sum() - ((team_df["sack_flag"] > 0) & team_df["is_sack"]).sum()
        )
        stats[team]["explosivePlays"] = int(
            pass_df["yards_gained_value"].ge(20).sum() + rush_df["yards_gained_value"].ge(10).sum()
        )

        if not is_empty_frame(team_epa_df) and "epa" in team_epa_df.columns:
            team_epa_df["epa"] = pd.to_numeric(team_epa_df["epa"], errors="coerce")
            pass_df["epa"] = pd.to_numeric(pass_df["epa"], errors="coerce")
            rush_df["epa"] = pd.to_numeric(rush_df["epa"], errors="coerce")
            stats[team]["passEpaPerPlay"] = pass_df["epa"].dropna().mean()
            stats[team]["rushEpaPerPlay"] = rush_df["epa"].dropna().mean()

        def extract_success_values(play_df: pd.DataFrame) -> pd.Series:
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
            stats[team]["passSuccessRate"] = pass_successes / pass_total
            stats[team]["passSuccessCounts"] = f"{pass_successes}/{pass_total}"
        if not is_empty_series(rush_success_values):
            rush_successes = int(rush_success_values.sum())
            rush_total = int(len(rush_success_values))
            stats[team]["rushSuccessRate"] = rush_successes / rush_total
            stats[team]["rushSuccessCounts"] = f"{rush_successes}/{rush_total}"

        fourth_down_df = team_epa_df[team_epa_df["down_value"].eq(4)].copy()
        fourth_down_success_values = extract_success_values(fourth_down_df)
        if not is_empty_series(fourth_down_success_values):
            fourth_down_successes = int(fourth_down_success_values.sum())
            fourth_down_total = int(len(fourth_down_success_values))
            stats[team]["fourthDownRate"] = fourth_down_successes / fourth_down_total
            stats[team]["fourthDownCounts"] = f"{fourth_down_successes}/{fourth_down_total}"

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

            stats[team]["redzoneTdTrips"] = f"{int(td_trips)}/{int(redzone_trips)}"
            stats[team]["redzoneEfficiency"] = (td_trips / redzone_trips) if redzone_trips else None

    return stats


def prepare_wp_data(game_df: pd.DataFrame) -> pd.DataFrame:
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


def build_rankings_week_labels(rankings_df: pd.DataFrame) -> tuple[list[dict[str, int]], pd.DataFrame]:
    week_points = (
        rankings_df[["season", "week"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["season", "week"])
        .reset_index(drop=True)
    )
    if week_points.empty:
        return [], pd.DataFrame()

    week_points["week_index"] = range(1, len(week_points) + 1)
    week_labels = [
        {
            "season": int(row["season"]),
            "week": int(row["week"]),
            "weekIndex": int(row["week_index"]),
        }
        for _, row in week_points.iterrows()
    ]
    return week_labels, week_points


def summarize_rankings_side(
    rankings_df: pd.DataFrame,
    side_col: str,
    week_labels: list[dict[str, int]],
    ascending: bool,
) -> pd.DataFrame:
    weekly = (
        rankings_df.groupby([side_col, "season", "week"], as_index=False)
        .agg(total_epa=("epa", "sum"), play_count=("epa", "size"))
    )
    weekly = weekly.rename(columns={side_col: "team"})
    team_week_grid = pd.DataFrame(
        [(team, label["season"], label["week"], label["weekIndex"]) for team in TEAM_OPTIONS for label in week_labels],
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


@lru_cache(maxsize=8)
def compute_cached_weekly_team_summaries(
    seasons_key: tuple[int, ...],
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int]], Optional[str]]:
    seasons = list(seasons_key)
    pbp_df, pbp_err = load_pbp_data(seasons_key)
    if is_empty_frame(pbp_df):
        return pd.DataFrame(), pd.DataFrame(), [], pbp_err

    required_cols = ["posteam", "defteam", "week", "season", "play_type", "epa"]
    if any(col not in pbp_df.columns for col in required_cols):
        return pd.DataFrame(), pd.DataFrame(), [], "Missing required play-by-play columns for team rankings."

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
        return pd.DataFrame(), pd.DataFrame(), [], None

    week_labels, week_points = build_rankings_week_labels(rankings_df)
    if week_points.empty:
        return pd.DataFrame(), pd.DataFrame(), [], None

    offense = summarize_rankings_side(rankings_df, "posteam", week_labels, ascending=False)
    defense = summarize_rankings_side(rankings_df, "defteam", week_labels, ascending=True)
    return offense, defense, week_labels, None


def build_rankings_dataset(
    offense: pd.DataFrame,
    defense: pd.DataFrame,
    week_labels: list[dict[str, int]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, int]]]:
    if offense.empty or defense.empty or not week_labels:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

    overall = offense.merge(
        defense[["team", "season", "week", "week_index", "cumulative_epa_per_play", "rank"]],
        on=["team", "season", "week", "week_index"],
        how="inner",
        suffixes=("_offense", "_defense"),
    )
    overall["average_rank"] = (overall["rank_offense"] + overall["rank_defense"]) / 2.0
    overall = overall.sort_values(
        ["week_index", "average_rank", "rank_offense", "team"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)
    overall["rank"] = overall.groupby("week_index").cumcount() + 1
    overall["cumulative_epa_per_play"] = -overall["average_rank"]

    return offense, defense, overall, week_labels


def serialize_game_row(row: pd.Series) -> dict[str, Any]:
    gameday = row.get("gameday")
    away_team = row["away_team"]
    home_team = row["home_team"]
    return {
        "gameId": str(row["game_id"]),
        "season": int(row["season"]) if pd.notna(row["season"]) else None,
        "week": int(row["week"]) if pd.notna(row["week"]) else None,
        "gameday": gameday.strftime("%Y-%m-%d") if pd.notna(gameday) else None,
        "gamedayLabel": gameday.strftime("%b %d, %Y") if pd.notna(gameday) else "Date unavailable",
        "gameType": row["game_type"],
        "seasonTypeLabel": SEASON_TYPE_LABELS.get(row["game_type"], row["game_type"]),
        "isPlayoff": bool(row["is_playoff"]),
        "homeTeam": home_team,
        "awayTeam": away_team,
        "displayHomeTeam": row.get("display_home_team", home_team),
        "displayAwayTeam": row.get("display_away_team", away_team),
        "displayHomeLogoUrl": logo_url(row.get("display_home_team", home_team)),
        "displayAwayLogoUrl": logo_url(row.get("display_away_team", away_team)),
        "homeScore": int(row["home_score"]) if pd.notna(row["home_score"]) else None,
        "awayScore": int(row["away_score"]) if pd.notna(row["away_score"]) else None,
        "wentOt": bool(row.get("went_ot", False)),
        "divisionHome": row.get("division_home"),
        "divisionAway": row.get("division_away"),
    }


def serialize_drive_summary(drive_df: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for index, row in drive_df.reset_index(drop=True).iterrows():
        rows.append(
            {
                "index": index,
                "drive": int(row["drive"]) if pd.notna(row["drive"]) else index + 1,
                "posteam": row["posteam"],
                "qtr": int(row["qtr"]),
                "yardlineStart": float(row["yardline_start"]),
                "yardlineEnd": float(row["yardline_end"]),
                "driveResult": str(row.get("drive_result", "") or "").upper(),
            }
        )
    return rows


def serialize_wp_data(wp_df: pd.DataFrame) -> dict[str, Any]:
    if wp_df.empty:
        return {"points": [], "quarters": []}

    play_qtr = wp_df.groupby("qtr", as_index=False).last()
    quarter_labels = ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "OT"]
    quarter_ranges = []
    quarter_starts = [0.0] + play_qtr["play_num_scaled"].iloc[:-1].tolist()
    quarter_ends = play_qtr["play_num_scaled"].tolist()
    for idx, (start_x, end_x) in enumerate(zip(quarter_starts, quarter_ends)):
        if idx >= len(quarter_labels):
            break
        quarter_ranges.append(
            {
                "label": quarter_labels[idx],
                "start": float(start_x),
                "end": float(end_x),
            }
        )

    points = [
        {
            "x": float(row["play_num_scaled"]),
            "homeWp": float(row["home_wp"]),
            "qtr": int(row["qtr"]),
        }
        for _, row in wp_df.iterrows()
    ]
    return {"points": points, "quarters": quarter_ranges}


def serialize_rankings_rows(ranking_df: pd.DataFrame) -> list[dict[str, Any]]:
    if ranking_df.empty:
        return []
    return [
        {
            "team": row["team"],
            "season": int(row["season"]),
            "week": int(row["week"]),
            "weekIndex": int(row["week_index"]),
            "rank": float(row["rank"]),
            "cumulativeEpaPerPlay": float(row["cumulative_epa_per_play"]),
        }
        for _, row in ranking_df.iterrows()
    ]


def make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def rankings_description(selected_season: int) -> str:
    return (
        f"Showing cumulative EPA per play rankings for the {selected_season} regular season. "
        "Offense ranks best-to-worst by higher EPA/play; defense ranks best-to-worst by lower EPA/play allowed; "
        "overall ranks by averaging each team's offensive and defensive ranks, with the better offensive rank breaking ties."
    )


def build_games_caption(view_mode: str, seasons: list[int], team1: Optional[str], team2: Optional[str]) -> str:
    start_season = seasons[0]
    end_season = seasons[-1]
    if view_mode == "matchup":
        return f"Showing {team1} vs {team2} from {start_season} through {end_season}."
    if view_mode == "team_games":
        return f"Showing all {team1} games from {start_season} through {end_season}."
    if view_mode == "team_primetime":
        return f"Showing all {team1} primetime games from {start_season} through {end_season}."
    if view_mode == "team_playoffs":
        return f"Showing all {team1} playoff games from {start_season} through {end_season}."
    if view_mode == "team_divisional":
        return f"Showing all {team1} divisional games from {start_season} through {end_season}."
    if view_mode == "divisional_games":
        return f"Showing all divisional games from {start_season} through {end_season}."
    if view_mode == "all_playoffs":
        return f"Showing all playoff games from {start_season} through {end_season}."
    if view_mode == "all_primetime":
        return f"Showing all primetime games from {start_season} through {end_season}."
    return f"Showing all completed games from {start_season} through {end_season}."


def get_meta_payload() -> dict[str, Any]:
    default_start, default_end = default_season_range()
    return {
        "pages": [{"label": label, "value": value} for label, value in APP_PAGES.items()],
        "viewModes": [{"label": label, "value": value} for label, value in VIEW_MODES.items()],
        "teams": [
            {
                "abbr": team,
                "name": TEAM_NAMES[team],
                "color": TEAM_COLORS[team],
                "logoUrl": logo_url(team),
                "division": TEAM_TO_DIVISION.get(team),
            }
            for team in TEAM_OPTIONS
        ],
        "config": {
            "minSeason": MIN_SEASON,
            "latestCompletedSeason": LATEST_COMPLETED_SEASON,
            "maxRankingsSeason": MAX_RANKINGS_SEASON,
            "defaultSeasonRange": [default_start, default_end],
            "defaultRankingsSeason": MAX_RANKINGS_SEASON,
            "pageSize": ALL_GAMES_PAGE_SIZE,
        },
    }


def get_games_payload(
    view_mode: str,
    start_season: int,
    end_season: int,
    team1: Optional[str] = None,
    team2: Optional[str] = None,
    page: int = 1,
) -> tuple[dict[str, Any], int]:
    seasons = list(range(start_season, end_season + 1))
    schedule_df, schedule_err = load_schedule_data(tuple(seasons))
    if schedule_df.empty:
        return {
            "error": f"Could not load schedule data for {start_season}-{end_season}. {schedule_err or ''}".strip(),
        }, 500

    team1 = canonical_team_abbr(team1) if team1 else None
    team2 = canonical_team_abbr(team2) if team2 else None
    matchup_games = prepare_game_catalog(schedule_df, view_mode, team1, team2)
    if matchup_games.empty:
        return {
            "caption": build_games_caption(view_mode, seasons, team1, team2),
            "games": [],
            "pagination": {
                "page": 1,
                "pageSize": ALL_GAMES_PAGE_SIZE,
                "totalPages": 1,
                "totalGames": 0,
                "isPaginated": view_mode in PAGINATED_VIEW_MODES,
            },
        }, 200

    total_games = len(matchup_games)
    total_pages = max(1, (total_games + ALL_GAMES_PAGE_SIZE - 1) // ALL_GAMES_PAGE_SIZE)
    current_page = max(1, min(page, total_pages))
    games_to_render = matchup_games
    if view_mode in PAGINATED_VIEW_MODES:
        page_start = (current_page - 1) * ALL_GAMES_PAGE_SIZE
        page_end = page_start + ALL_GAMES_PAGE_SIZE
        games_to_render = matchup_games.iloc[page_start:page_end].reset_index(drop=True)

    games = [serialize_game_row(row) for _, row in games_to_render.iterrows()]
    return {
        "caption": build_games_caption(view_mode, seasons, team1, team2),
        "games": games,
        "pagination": {
            "page": current_page,
            "pageSize": ALL_GAMES_PAGE_SIZE,
            "totalPages": total_pages,
            "totalGames": total_games,
            "startIndex": ((current_page - 1) * ALL_GAMES_PAGE_SIZE) + 1 if total_games else 0,
            "endIndex": min(current_page * ALL_GAMES_PAGE_SIZE, total_games),
            "isPaginated": view_mode in PAGINATED_VIEW_MODES,
        },
    }, 200


def get_game_details_payload(
    selected_game: dict[str, Any],
    team1: Optional[str] = None,
    team2: Optional[str] = None,
) -> tuple[dict[str, Any], int]:
    selected_season = int(selected_game["season"])
    pbp_df, pbp_err = load_pbp_data((selected_season,))
    if is_empty_frame(pbp_df):
        return {
            "error": f"Could not load play-by-play data for {selected_season}. {pbp_err or ''}".strip(),
        }, 500

    if "game_id" not in pbp_df.columns:
        return {"error": "The loaded play-by-play data does not include a `game_id` column."}, 500

    game_df = pbp_df[pbp_df["game_id"].astype(str) == str(selected_game["gameId"])].copy()
    if game_df.empty:
        return {"error": "No play-by-play rows were found for the selected game."}, 404

    drive_final = build_drive_summary(game_df)
    if drive_final.empty:
        return {"error": "No drive data was available to draw the visualization for this game."}, 500

    normalized_game = {
        **selected_game,
        "awayTeam": canonical_team_abbr(selected_game["awayTeam"]),
        "homeTeam": canonical_team_abbr(selected_game["homeTeam"]),
    }
    viz_team1 = normalized_game["awayTeam"]
    viz_team2 = normalized_game["homeTeam"]

    stats = compute_game_stats(game_df, normalized_game)
    wp_df = prepare_wp_data(game_df)
    quarter_count = min(drive_final["qtr"].dropna().nunique(), len(QUARTER_COLORS))
    quarter_colors = QUARTER_COLORS[: max(quarter_count, 1)]
    return {
        "selectedGame": normalized_game,
        "vizTeam1": viz_team1,
        "vizTeam2": viz_team2,
        "quarterColors": quarter_colors,
        "driveSummary": serialize_drive_summary(drive_final),
        "winProbability": serialize_wp_data(wp_df),
        "stats": make_json_safe(stats),
    }, 200


def get_rankings_payload(season: int) -> tuple[dict[str, Any], int]:
    offense_rankings, defense_rankings, week_labels, pbp_err = compute_cached_weekly_team_summaries((season,))
    if offense_rankings.empty or defense_rankings.empty:
        if pbp_err:
            return {"error": f"Could not load play-by-play data for {season}. {pbp_err}"}, 500
        return {"error": f"No pass/run play data was available to build team rankings for {season}."}, 404

    offense_rankings, defense_rankings, overall_rankings, week_labels = build_rankings_dataset(
        offense_rankings,
        defense_rankings,
        week_labels,
    )
    if offense_rankings.empty or defense_rankings.empty or overall_rankings.empty:
        return {"error": f"No pass/run play data was available to build team rankings for {season}."}, 404

    return {
        "season": season,
        "description": rankings_description(season),
        "weekLabels": week_labels,
        "offense": serialize_rankings_rows(offense_rankings),
        "defense": serialize_rankings_rows(defense_rankings),
        "overall": serialize_rankings_rows(overall_rankings),
    }, 200
