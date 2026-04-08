import { formatPercentage, formatSigned, formatWhole } from "../lib/utils";

function StatRow({ label, awayValue, homeValue, awayColor, homeColor }) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_minmax(56px,auto)_minmax(56px,auto)] items-center gap-2 border-t border-slate-900/8 py-2.5 sm:grid-cols-[minmax(0,1fr)_minmax(72px,auto)_minmax(72px,auto)] sm:gap-3 sm:py-3">
      <div className="min-w-0 text-xs text-slate-600 sm:text-sm">{label}</div>
      <div className="text-center text-xs font-bold sm:text-sm" style={{ color: awayColor }}>
        {awayValue}
      </div>
      <div className="text-center text-xs font-bold sm:text-sm" style={{ color: homeColor }}>
        {homeValue}
      </div>
    </div>
  );
}

function TeamHeader({ team, displayTeam, teamsByAbbr }) {
  const meta = teamsByAbbr[team];

  return (
    <div className="text-center">
      <img src={meta?.logoUrl} alt={meta?.name || team} className="mx-auto h-10 w-10 object-contain sm:h-14 sm:w-14" />
      <p className="mt-2 text-xs font-bold sm:text-sm" style={{ color: meta?.color || "#334155" }}>
        {displayTeam}
      </p>
    </div>
  );
}

function formatRate(rate, counts) {
  if (rate === null || rate === undefined) {
    return `— (${counts || "0/0"})`;
  }
  return `${formatPercentage(rate * 100)} (${counts || "0/0"})`;
}

export default function StatsComparisonCard({ stats, selectedGame, teamsByAbbr }) {
  const away = stats[selectedGame.awayTeam] || {};
  const home = stats[selectedGame.homeTeam] || {};
  const awayColor = teamsByAbbr[selectedGame.awayTeam]?.color || "#334155";
  const homeColor = teamsByAbbr[selectedGame.homeTeam]?.color || "#334155";

  const rows = [
    ["Total Plays", formatWhole(away.totalPlays), formatWhole(home.totalPlays)],
    ["Passing Yards", formatWhole(away.passingYards), formatWhole(home.passingYards)],
    ["Rushing Yards", formatWhole(away.rushingYards), formatWhole(home.rushingYards)],
    ["Passing EPA / Play", formatSigned(away.passEpaPerPlay), formatSigned(home.passEpaPerPlay)],
    ["Rushing EPA / Play", formatSigned(away.rushEpaPerPlay), formatSigned(home.rushEpaPerPlay)],
    [
      "Pass Success Rate",
      formatRate(away.passSuccessRate, away.passSuccessCounts),
      formatRate(home.passSuccessRate, home.passSuccessCounts),
    ],
    [
      "Rush Success Rate",
      formatRate(away.rushSuccessRate, away.rushSuccessCounts),
      formatRate(home.rushSuccessRate, home.rushSuccessCounts),
    ],
    ["Turnovers", formatWhole(away.turnovers), formatWhole(home.turnovers)],
    ["Sacks Allowed", formatWhole(away.sacksAllowed), formatWhole(home.sacksAllowed)],
    [
      "Fourth Down Rate",
      formatRate(away.fourthDownRate, away.fourthDownCounts),
      formatRate(home.fourthDownRate, home.fourthDownCounts),
    ],
    ["Explosive Plays", formatWhole(away.explosivePlays), formatWhole(home.explosivePlays)],
    [
      "Redzone Efficiency",
      formatRate(away.redzoneEfficiency, away.redzoneTdTrips),
      formatRate(home.redzoneEfficiency, home.redzoneTdTrips),
    ],
  ];

  return (
    <aside className="surface-card min-w-0 overflow-hidden rounded-[2rem] bg-[#f7f8f2] p-4 sm:p-5">
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 border-b border-slate-900/8 pb-4 sm:gap-4">
        <TeamHeader team={selectedGame.awayTeam} displayTeam={selectedGame.displayAwayTeam} teamsByAbbr={teamsByAbbr} />
        <span className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500 sm:text-sm sm:tracking-[0.24em]">vs</span>
        <TeamHeader team={selectedGame.homeTeam} displayTeam={selectedGame.displayHomeTeam} teamsByAbbr={teamsByAbbr} />
      </div>

      <div className="mt-2">
        {rows.map(([label, awayValue, homeValue]) => (
          <StatRow
            key={label}
            label={label}
            awayValue={awayValue}
            homeValue={homeValue}
            awayColor={awayColor}
            homeColor={homeColor}
          />
        ))}
      </div>
    </aside>
  );
}
