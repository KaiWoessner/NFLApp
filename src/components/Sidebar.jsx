import { useEffect, useState } from "react";
import { cn } from "../lib/utils";
import MatchupPicker from "./MatchupPicker";
import TeamPicker, { nflLogoUrl } from "./TeamPicker";

const ONE_TEAM_MODES = new Set([
  "team_games",
  "team_primetime",
  "team_playoffs",
  "team_divisional",
]);

const HIDDEN_VIEW_MODES = new Set([
  "all_games",
  "all_primetime",
  "all_playoffs",
  "divisional_games",
]);

const VIEW_MODE_LABELS = {
  team_games: "All Games",
  team_primetime: "Primetime Games",
  team_playoffs: "Playoff Games",
  team_divisional: "Divisional Games",
};

function SeasonRangeSlider({ minSeason, maxSeason, value, onChange }) {
  const [startSeason, endSeason] = value;
  const span = Math.max(1, maxSeason - minSeason);
  const startPercent = ((startSeason - minSeason) / span) * 100;
  const endPercent = ((endSeason - minSeason) / span) * 100;

  function updateStart(nextStart) {
    onChange([Math.min(nextStart, endSeason), endSeason]);
  }

  function updateEnd(nextEnd) {
    onChange([startSeason, Math.max(nextEnd, startSeason)]);
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between text-sm text-[#f1eadc]">
        <span>{startSeason}</span>
        <span>{endSeason}</span>
      </div>

      <div className="relative h-10">
        <div className="absolute left-0 right-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-[#2b342d]" />
        <div
          className="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-[#7f9547]"
          style={{
            left: `${startPercent}%`,
            width: `${Math.max(0, endPercent - startPercent)}%`,
          }}
        />

        <input
          type="range"
          min={minSeason}
          max={maxSeason}
          value={startSeason}
          onChange={(event) => updateStart(Number(event.target.value))}
          className="season-slider pointer-events-none absolute inset-0 z-10 h-10 w-full appearance-none bg-transparent"
          aria-label="Start season"
        />
        <input
          type="range"
          min={minSeason}
          max={maxSeason}
          value={endSeason}
          onChange={(event) => updateEnd(Number(event.target.value))}
          className="season-slider absolute inset-0 h-10 w-full appearance-none bg-transparent"
          aria-label="End season"
        />
      </div>
    </div>
  );
}

export default function Sidebar({
  meta,
  apiReady,
  appPage,
  onPageChange,
  viewMode,
  onViewModeChange,
  team1,
  onTeam1Change,
  team2,
  onTeam2Change,
  singleModeTeams,
  onSingleModeTeamChange,
  seasonRange,
  onSeasonRangeChange,
  rankingSeason,
  onRankingSeasonChange,
}) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const nextPageLabel = appPage === "game_explorer" ? "Team Rankings" : "Game Explorer";
  const viewModes = (meta?.viewModes || []).filter((mode) => !HIDDEN_VIEW_MODES.has(mode.value));
  const teams = meta?.teams || [];
  const config = meta?.config;
  const rankingSeasons = [];

  useEffect(() => {
    setMobileOpen(false);
  }, [appPage, viewMode]);

  if (config) {
    for (let season = config.maxRankingsSeason; season >= config.minSeason; season -= 1) {
      rankingSeasons.push(season);
    }
  }

  function teamLogoForMode(modeValue) {
    const selectedTeam = teams.find((team) => team.abbr === (singleModeTeams?.[modeValue] || ""));
    return {
      alt: selectedTeam ? selectedTeam.name : "NFL",
      url: selectedTeam?.logoUrl || nflLogoUrl(),
    };
  }

  function matchupLogo(teamAbbr) {
    const selectedTeam = teams.find((team) => team.abbr === teamAbbr);
    return {
      alt: selectedTeam ? selectedTeam.name : "NFL",
      url: selectedTeam?.logoUrl || nflLogoUrl(),
    };
  }

  function viewModeLabel(mode) {
    return VIEW_MODE_LABELS[mode.value] || mode.label;
  }

  function handleOpenView(nextViewMode) {
    onViewModeChange(nextViewMode);
    setMobileOpen(false);
  }

  const sidebarInner = (
    <>
      <div className="mb-6 rounded-[2rem] border border-[#2b342d] bg-[#202621]/92 p-5 shadow-sm">
        <p className="mb-2 text-xs uppercase tracking-[0.28em] text-[#82984d]">NFL React</p>
        <h1 className="font-display text-3xl leading-none text-[#f7f2e8]">Game Explorer</h1>
      </div>

      <button
        type="button"
        onClick={() => onPageChange(appPage === "game_explorer" ? "team_rankings" : "game_explorer")}
        disabled={!apiReady}
        className="mb-8 w-full rounded-2xl border border-[#43562b] bg-[#2b3722] px-4 py-3 text-sm font-semibold text-[#ece6d8] transition hover:bg-[#334128]"
      >
        Switch to {nextPageLabel}
      </button>

      {!apiReady ? (
        <section className="rounded-3xl border border-[#2b342d] bg-[#202621]/92 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-[0.22em] text-[#a3a89d]">Backend</p>
          <p className="mt-3 text-sm leading-6 text-[#ddd7ca]">
            The sidebar controls unlock after the Flask API responds. Start the backend on port `5001` and refresh the page.
          </p>
        </section>
      ) : null}

      {apiReady && appPage === "game_explorer" ? (
        <div className="space-y-4">
          <section>
            <p className="mb-2 text-xs uppercase tracking-[0.22em] text-[#c9cbc2]">View</p>
            <div className="grid gap-2">
              {viewModes.map((mode) => (
                mode.value === "matchup" ? (
                  <div
                    key={mode.value}
                    className={cn(
                      "grid grid-cols-[minmax(0,1fr)_40px_auto_auto] items-center gap-2 rounded-2xl border px-3 py-2 text-sm transition",
                      viewMode === mode.value
                        ? "border-[#43562b] bg-[#2b3722] text-[#ece6d8]"
                        : "border-[#2b342d] bg-[#202621]/92 text-[#d7d3c9]",
                    )}
                  >
                    <div className="min-w-0 flex-1 text-left font-medium">{viewModeLabel(mode)}</div>
                    <div className="relative h-12 w-10 justify-self-center">
                      <img
                        src={matchupLogo(team1).url}
                        alt={matchupLogo(team1).alt}
                        className="absolute left-1/2 top-0 h-6 w-6 -translate-x-1/2 object-contain"
                      />
                      <img
                        src={matchupLogo(team2).url}
                        alt={matchupLogo(team2).alt}
                        className="absolute bottom-0 left-1/2 h-6 w-6 -translate-x-1/2 object-contain"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => handleOpenView(mode.value)}
                      className={cn(
                        "shrink-0 rounded-xl border px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] transition",
                        viewMode === mode.value
                          ? "border-[#7f9547] bg-[#344226] text-[#f2ecdf]"
                          : "border-[#2f382f] bg-[#1f2520] text-[#d4d2ca] hover:bg-[#262d26] hover:text-[#f7f2e8]",
                      )}
                    >
                      Open
                    </button>
                    <MatchupPicker
                      teams={teams}
                      team1={team1}
                      team2={team2}
                      onChange={(nextTeam1, nextTeam2) => {
                        onTeam1Change(nextTeam1);
                        onTeam2Change(nextTeam2);
                        handleOpenView("matchup");
                      }}
                    />
                  </div>
                ) : ONE_TEAM_MODES.has(mode.value) ? (
                  <div
                    key={mode.value}
                    className={cn(
                      "grid grid-cols-[minmax(0,1fr)_40px_auto_auto] items-center gap-2 rounded-2xl border px-3 py-2.5 text-sm transition",
                      viewMode === mode.value
                        ? "border-[#43562b] bg-[#2b3722] text-[#ece6d8]"
                        : "border-[#2b342d] bg-[#202621]/92 text-[#d7d3c9]",
                    )}
                  >
                    <div className="min-w-0 flex-1 text-left font-medium">{viewModeLabel(mode)}</div>
                    <img
                      src={teamLogoForMode(mode.value).url}
                      alt={teamLogoForMode(mode.value).alt}
                      className="h-9 w-9 shrink-0 justify-self-center object-contain"
                    />
                    <button
                      type="button"
                      onClick={() => handleOpenView(mode.value)}
                      className={cn(
                        "shrink-0 rounded-xl border px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] transition",
                        viewMode === mode.value
                          ? "border-[#7f9547] bg-[#344226] text-[#f2ecdf]"
                          : "border-[#2f382f] bg-[#1f2520] text-[#d4d2ca] hover:bg-[#262d26] hover:text-[#f7f2e8]",
                      )}
                    >
                      Open
                    </button>
                    <TeamPicker
                      title="Team"
                      teams={teams}
                      value={singleModeTeams?.[mode.value] || ""}
                      onChange={(nextTeam) => {
                        onSingleModeTeamChange(mode.value, nextTeam);
                        handleOpenView(mode.value);
                      }}
                      variant="button"
                    />
                  </div>
                ) : (
                  <button
                    key={mode.value}
                    type="button"
                    onClick={() => handleOpenView(mode.value)}
                    className={cn(
                      "rounded-2xl border px-4 py-3 text-left text-sm transition",
                      viewMode === mode.value
                        ? "border-[#43562b] bg-[#2b3722] text-[#ece6d8]"
                        : "border-[#2b342d] bg-[#202621]/92 text-[#d7d3c9] hover:bg-[#252d25] hover:text-[#f7f2e8]",
                    )}
                  >
                    {viewModeLabel(mode)}
                  </button>
                )
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-[#2b342d] bg-[#202621]/92 p-3 shadow-sm">
            <div className="mb-2 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.22em] text-[#858981]">Season Range</p>
                <p className="mt-0.5 text-sm text-[#f1eadc]">Choose start and end seasons</p>
              </div>
            </div>

            <SeasonRangeSlider
              minSeason={config?.minSeason || seasonRange[0]}
              maxSeason={config?.latestCompletedSeason || seasonRange[1]}
              value={seasonRange}
              onChange={onSeasonRangeChange}
            />
          </section>
        </div>
      ) : null}

      {apiReady && appPage !== "game_explorer" ? (
        <section className="rounded-3xl border border-[#2b342d] bg-[#202621]/92 p-4 shadow-sm">
          <p className="mb-3 text-xs uppercase tracking-[0.22em] text-[#a3a89d]">Season</p>
          <select
            value={rankingSeason || ""}
            onChange={(event) => onRankingSeasonChange(Number(event.target.value))}
            className="w-full rounded-2xl border border-[#2f382f] bg-[#1f2520] px-4 py-3 text-[#f7f2e8] outline-none transition focus:border-[#7f9547]"
          >
            {rankingSeasons.map((season) => (
              <option key={season} value={season}>
                {season}
              </option>
            ))}
          </select>
        </section>
      ) : null}
    </>
  );

  return (
    <>
      <div className="sidebar-panel border-b border-[#2b342d] px-4 py-3 text-[#f1eadc] lg:hidden">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.28em] text-[#82984d]">NFL React</p>
            <p className="mt-1 font-display text-2xl leading-none text-[#f7f2e8]">Game Explorer</p>
          </div>
          <button
            type="button"
            onClick={() => setMobileOpen((current) => !current)}
            className="rounded-2xl border border-[#43562b] bg-[#2b3722] px-4 py-2.5 text-xs font-semibold uppercase tracking-[0.18em] text-[#ece6d8] transition hover:bg-[#334128]"
          >
            {mobileOpen ? "Hide Filters" : "Show Filters"}
          </button>
        </div>
      </div>

      {mobileOpen ? (
        <div className="sidebar-panel thin-scrollbar border-b border-[#2b342d] px-4 py-4 text-[#f1eadc] lg:hidden">
          {sidebarInner}
        </div>
      ) : null}

      <div className="sidebar-panel hidden lg:block">
        <aside className="thin-scrollbar sticky top-0 h-screen overflow-y-auto px-5 py-6 text-[#f1eadc] lg:px-6">
          {sidebarInner}
        </aside>
      </div>
    </>
  );
}
