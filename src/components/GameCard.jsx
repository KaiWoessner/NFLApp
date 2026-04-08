function TeamBadge({ logoUrl, label }) {
  return (
    <div className="flex min-w-0 flex-col items-center gap-1.5">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900/5 sm:h-16 sm:w-16 sm:rounded-3xl">
        <img src={logoUrl} alt={label} className="h-8 w-8 object-contain sm:h-11 sm:w-11" />
      </div>
      <span className="text-[11px] font-semibold tracking-[0.18em] text-slate-700 sm:text-xs">{label}</span>
    </div>
  );
}

export default function GameCard({ game, teamsByAbbr, onExplore }) {
  const awayColor = teamsByAbbr[game.awayTeam]?.color || "#374151";
  const homeColor = teamsByAbbr[game.homeTeam]?.color || "#374151";

  return (
    <article className="surface-card rounded-[2rem] p-4 transition hover:-translate-y-0.5 sm:p-5">
      <div className="grid grid-cols-[1.05fr_1fr_0.78fr] items-center gap-3 sm:gap-5">
          <div className="flex min-w-0 items-center justify-center gap-2 sm:gap-4">
            <TeamBadge logoUrl={game.displayAwayLogoUrl} label={game.displayAwayTeam} />
            <span className="rounded-full bg-slate-900/6 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 sm:px-3 sm:text-xs">
              vs
            </span>
            <TeamBadge logoUrl={game.displayHomeLogoUrl} label={game.displayHomeTeam} />
          </div>

          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-900 sm:text-base">
              Week {game.week} • {game.season}
            </p>
            <p className="mt-1 text-[10px] uppercase tracking-[0.16em] text-slate-500 sm:text-xs">{game.seasonTypeLabel}</p>
            <p className="mt-1.5 text-xs text-slate-600 sm:text-sm">{game.gamedayLabel}</p>
          </div>

          <div className="flex min-w-0 flex-col items-end justify-between gap-4">
            <div className="text-right">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
                {game.wentOt ? "Final OT" : "Final"}
              </p>
              <p className="mt-1 text-2xl font-black tracking-tight text-slate-900 sm:text-3xl">
                <span style={{ color: awayColor }}>{game.awayScore}</span>
                <span className="px-1 text-slate-400">-</span>
                <span style={{ color: homeColor }}>{game.homeScore}</span>
              </p>
            </div>

            <button
              type="button"
              onClick={() => onExplore(game)}
              className="rounded-2xl bg-slate-950 px-3 py-2 text-xs font-semibold text-white transition hover:bg-slate-800 sm:px-4 sm:py-2.5 sm:text-sm"
            >
              Explore
            </button>
          </div>
      </div>
    </article>
  );
}
