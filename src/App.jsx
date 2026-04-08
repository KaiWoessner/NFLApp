import { useEffect, useMemo, useState } from "react";
import GameCard from "./components/GameCard";
import DriveChartCard from "./components/DriveChartCard";
import Modal from "./components/Modal";
import PaginationBar from "./components/PaginationBar";
import RankingsChart from "./components/RankingsChart";
import Sidebar from "./components/Sidebar";
import StatsComparisonCard from "./components/StatsComparisonCard";
import WinProbabilityChart from "./components/WinProbabilityChart";
import { fetchGameDetails, fetchGames, fetchMeta, fetchRankings } from "./lib/api";
import { buildGameDetailTitle, clamp, cn } from "./lib/utils";

const ONE_TEAM_MODES = new Set([
  "team_games",
  "team_primetime",
  "team_playoffs",
  "team_divisional",
]);

const SINGLE_MODE_ALL_VIEW = {
  team_games: "all_games",
  team_primetime: "all_primetime",
  team_playoffs: "all_playoffs",
  team_divisional: "divisional_games",
};

const RANKING_TABS = [
  { key: "offense", label: "Offense Rankings", title: "Offensive Rankings", subtitle: "Cumulative offensive EPA / play" },
  { key: "defense", label: "Defense Rankings", title: "Defensive Rankings", subtitle: "Cumulative defensive EPA / play allowed" },
  { key: "overall", label: "Overall Rankings", title: "Overall Rankings", subtitle: "Average of offensive and defensive ranks; offense wins ties" },
];

function LoadingBlock({ label }) {
  return (
    <div className="surface-card rounded-[2rem] p-6">
      <p className="text-sm text-slate-600">{label}</p>
    </div>
  );
}

function MessageBlock({ title, tone = "info" }) {
  const toneClasses =
    tone === "error"
      ? "border-red-200 bg-red-50 text-red-800"
      : tone === "warning"
        ? "border-amber-200 bg-amber-50 text-amber-900"
        : "border-slate-200 bg-white text-slate-700";

  return (
    <div className={cn("rounded-[2rem] border px-5 py-4 text-sm", toneClasses)}>
      {title}
    </div>
  );
}

export default function App() {
  const [meta, setMeta] = useState(null);
  const [metaLoading, setMetaLoading] = useState(true);
  const [metaError, setMetaError] = useState("");
  const [appPage, setAppPage] = useState("game_explorer");
  const [viewMode, setViewMode] = useState("all_games");
  const [team1, setTeam1] = useState("");
  const [team2, setTeam2] = useState("");
  const [singleModeTeams, setSingleModeTeams] = useState({
    team_games: "",
    team_primetime: "",
    team_playoffs: "",
    team_divisional: "",
  });
  const [seasonRange, setSeasonRange] = useState([2024, 2025]);
  const [rankingSeason, setRankingSeason] = useState(2025);
  const [page, setPage] = useState(1);
  const [gamesState, setGamesState] = useState({ loading: false, error: "", data: null });
  const [selectedGameId, setSelectedGameId] = useState("");
  const [detailState, setDetailState] = useState({ open: false, loading: false, error: "", data: null });
  const [rankingsState, setRankingsState] = useState({ loading: false, error: "", data: null });
  const [rankingsTab, setRankingsTab] = useState("offense");

  function handleSeasonRangeChange(nextRange) {
    if (!Array.isArray(nextRange) || nextRange.length !== 2) {
      return;
    }

    const start = Number(nextRange[0]);
    const end = Number(nextRange[1]);

    if (!Number.isFinite(start) || !Number.isFinite(end)) {
      return;
    }

    setSeasonRange([Math.min(start, end), Math.max(start, end)]);
  }

  useEffect(() => {
    const controller = new AbortController();

    setMetaLoading(true);
    fetchMeta(controller.signal)
      .then((payload) => {
        setMeta(payload);
        handleSeasonRangeChange(payload.config.defaultSeasonRange);
        setRankingSeason(payload.config.defaultRankingsSeason);
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setMetaError(error.message);
        }
      })
      .finally(() => setMetaLoading(false));

    return () => controller.abort();
  }, []);

  const teamsByAbbr = useMemo(
    () => Object.fromEntries((meta?.teams || []).map((team) => [team.abbr, team])),
    [meta],
  );

  const normalizedSeasonRange = useMemo(() => {
    if (!meta?.config) {
      return seasonRange;
    }
    const start = clamp(seasonRange[0], meta.config.minSeason, meta.config.latestCompletedSeason);
    const end = clamp(seasonRange[1], meta.config.minSeason, meta.config.latestCompletedSeason);
    return start <= end ? [start, end] : [end, start];
  }, [meta, seasonRange]);

  const activeTeam1 = useMemo(() => {
    if (viewMode === "matchup") {
      return team1;
    }

    if (ONE_TEAM_MODES.has(viewMode)) {
      return singleModeTeams[viewMode] || "";
    }

    return "";
  }, [singleModeTeams, team1, viewMode]);

  const activeTeam2 = viewMode === "matchup" ? team2 : "";
  const effectiveViewMode =
    ONE_TEAM_MODES.has(viewMode) && !activeTeam1 ? SINGLE_MODE_ALL_VIEW[viewMode] || viewMode : viewMode;

  function handleSingleModeTeamChange(mode, nextTeam) {
    setSingleModeTeams((current) => ({ ...current, [mode]: nextTeam }));
  }

  useEffect(() => {
    setPage(1);
    setDetailState({ open: false, loading: false, error: "", data: null });
  }, [viewMode, team1, team2, singleModeTeams, normalizedSeasonRange[0], normalizedSeasonRange[1], appPage]);

  const validationMessage = useMemo(() => {
    if (appPage !== "game_explorer") {
      return null;
    }

    if (viewMode === "matchup" && (!activeTeam1 || !activeTeam2)) {
      return { tone: "info", title: "Choose two teams from the logo pickers to load matchup history." };
    }

    if (viewMode === "matchup" && activeTeam1 && activeTeam2 && activeTeam1 === activeTeam2) {
      return { tone: "warning", title: "Choose two different teams." };
    }

    return null;
  }, [activeTeam1, activeTeam2, appPage, viewMode]);

  useEffect(() => {
    if (!meta || appPage !== "game_explorer" || validationMessage) {
      return undefined;
    }

    const controller = new AbortController();
    setGamesState((current) => ({ ...current, loading: true, error: "" }));

    fetchGames(
      {
        viewMode: effectiveViewMode,
        team1: activeTeam1,
        team2: activeTeam2,
        startSeason: normalizedSeasonRange[0],
        endSeason: normalizedSeasonRange[1],
        page,
      },
      controller.signal,
    )
      .then((payload) => setGamesState({ loading: false, error: "", data: payload }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setGamesState({ loading: false, error: error.message, data: null });
        }
      });

    return () => controller.abort();
  }, [activeTeam1, activeTeam2, appPage, effectiveViewMode, meta, normalizedSeasonRange, page, validationMessage, viewMode]);

  useEffect(() => {
    if (appPage !== "team_rankings" || !rankingSeason) {
      return undefined;
    }

    const controller = new AbortController();
    setRankingsState({ loading: true, error: "", data: null });

    fetchRankings(rankingSeason, controller.signal)
      .then((payload) => setRankingsState({ loading: false, error: "", data: payload }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setRankingsState({ loading: false, error: error.message, data: null });
        }
      });

    return () => controller.abort();
  }, [appPage, rankingSeason]);

  useEffect(() => {
    const games = gamesState.data?.games || [];
    if (!games.length) {
      setSelectedGameId("");
      return;
    }

    if (!games.some((game) => game.gameId === selectedGameId)) {
      setSelectedGameId(games[0].gameId);
    }
  }, [gamesState.data, selectedGameId]);

  const selectedGame = useMemo(
    () => (gamesState.data?.games || []).find((game) => game.gameId === selectedGameId) || null,
    [gamesState.data, selectedGameId],
  );

  async function openGameDetails(game) {
    setSelectedGameId(game.gameId);
    setDetailState({ open: true, loading: true, error: "", data: null });

    const controller = new AbortController();
    try {
      const payload = await fetchGameDetails(
        { selectedGame: game, team1: activeTeam1, team2: activeTeam2 },
        controller.signal,
      );
      setDetailState({ open: true, loading: false, error: "", data: payload });
    } catch (error) {
      setDetailState({ open: true, loading: false, error: error.message, data: null });
    }
  }

  function closeModal() {
    setDetailState({ open: false, loading: false, error: "", data: null });
  }

  const activeRanking = rankingsState.data?.[rankingsTab] || [];
  const activeRankingMeta = RANKING_TABS.find((tab) => tab.key === rankingsTab);
  const apiReady = Boolean(meta?.config);

  return (
    <div className="app-shell min-h-screen overflow-x-hidden lg:grid lg:grid-cols-[340px_minmax(0,1fr)]">
      <Sidebar
        meta={meta}
        apiReady={apiReady}
        appPage={appPage}
        onPageChange={setAppPage}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        team1={team1}
        onTeam1Change={setTeam1}
        team2={team2}
        onTeam2Change={setTeam2}
        singleModeTeams={singleModeTeams}
        onSingleModeTeamChange={handleSingleModeTeamChange}
        seasonRange={normalizedSeasonRange}
        onSeasonRangeChange={handleSeasonRangeChange}
        rankingSeason={rankingSeason}
        onRankingSeasonChange={setRankingSeason}
      />

      <main className="min-h-screen overflow-x-hidden px-4 py-5 sm:px-6 lg:px-8 lg:py-8 xl:px-10">
        {metaLoading ? (
          <LoadingBlock label="Loading app metadata..." />
        ) : metaError ? (
          <div className="space-y-4">
            <MessageBlock title={metaError} tone="error" />
            <MessageBlock
              title="Start the backend with: cd backend && python3.10 app.py"
              tone="info"
            />
          </div>
        ) : (
          <div className="mx-auto max-w-[1500px]">
            <header className="mb-6">
              <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                {appPage === "team_rankings" ? "Power Curves" : "Historical Search"}
              </p>
              <h1 className="mt-2 font-display text-4xl leading-none text-slate-950 sm:text-5xl">
                {appPage === "team_rankings" ? "NFL Team Rankings" : "NFL Game Explorer"}
              </h1>
            </header>

            {appPage === "team_rankings" ? (
              <section className="space-y-5">
                {rankingsState.loading ? <LoadingBlock label="Loading play-by-play for team rankings..." /> : null}
                {rankingsState.error ? <MessageBlock title={rankingsState.error} tone="error" /> : null}

                {rankingsState.data ? (
                  <>
                    <p className="max-w-5xl text-sm leading-6 text-slate-600">{rankingsState.data.description}</p>

                    <div className="flex flex-wrap gap-3">
                      {RANKING_TABS.map((tab) => (
                        <button
                          key={tab.key}
                          type="button"
                          onClick={() => setRankingsTab(tab.key)}
                          className={cn(
                            "rounded-full px-4 py-2 text-sm font-semibold transition",
                            rankingsTab === tab.key
                              ? "bg-slate-950 text-white"
                              : "border border-slate-900/10 bg-white text-slate-700 hover:bg-slate-50",
                          )}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>

                    <RankingsChart
                      title={`${rankingsState.data.season} ${activeRankingMeta.title}`}
                      subtitle={activeRankingMeta.subtitle}
                      data={activeRanking}
                      weekLabels={rankingsState.data.weekLabels}
                      teamsByAbbr={teamsByAbbr}
                    />
                  </>
                ) : null}
              </section>
            ) : (
              <section className="space-y-5">
                {validationMessage ? <MessageBlock title={validationMessage.title} tone={validationMessage.tone} /> : null}
                {!validationMessage && gamesState.loading ? <LoadingBlock label="Loading matchup history..." /> : null}
                {!validationMessage && gamesState.error ? <MessageBlock title={gamesState.error} tone="error" /> : null}

                {!validationMessage && gamesState.data ? (
                  <>
                    <p className="text-sm leading-6 text-slate-600">{gamesState.data.caption}</p>

                    {gamesState.data.games.length === 0 ? (
                      <MessageBlock title="No completed games were found for the selected view in that range." tone="warning" />
                    ) : (
                      <>
                        <PaginationBar pagination={gamesState.data.pagination} onPageChange={setPage} />

                        <div className="grid gap-5 2xl:grid-cols-2">
                          {gamesState.data.games.map((game) => (
                            <GameCard
                              key={game.gameId}
                              game={game}
                              teamsByAbbr={teamsByAbbr}
                              onExplore={openGameDetails}
                            />
                          ))}
                        </div>
                      </>
                    )}
                  </>
                ) : null}
              </section>
            )}
          </div>
        )}
      </main>

      <Modal open={detailState.open} title={buildGameDetailTitle(detailState.data?.selectedGame || selectedGame)} onClose={closeModal}>
        {detailState.loading ? (
          <LoadingBlock label="Loading play-by-play for the selected game..." />
        ) : detailState.error ? (
          <MessageBlock title={detailState.error} tone="error" />
        ) : detailState.data ? (
          <div className="grid grid-cols-[minmax(0,2fr)_240px] gap-6 max-[920px]:grid-cols-1 lg:grid-cols-[minmax(0,1.95fr)_280px] xl:grid-cols-[minmax(0,1.9fr)_320px]">
            <div className="space-y-6">
              <DriveChartCard
                selectedGame={detailState.data.selectedGame}
                driveSummary={detailState.data.driveSummary}
                quarterColors={detailState.data.quarterColors}
                vizTeam1={detailState.data.vizTeam1}
                vizTeam2={detailState.data.vizTeam2}
                teamsByAbbr={teamsByAbbr}
              />
              <WinProbabilityChart
                selectedGame={detailState.data.selectedGame}
                winProbability={detailState.data.winProbability}
                teamsByAbbr={teamsByAbbr}
              />
            </div>

            <StatsComparisonCard
              stats={detailState.data.stats}
              selectedGame={detailState.data.selectedGame}
              teamsByAbbr={teamsByAbbr}
            />
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
