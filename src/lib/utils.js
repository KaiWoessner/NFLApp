export function cn(...values) {
  return values.filter(Boolean).join(" ");
}

export function formatPercentage(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return `${Number(value).toFixed(digits)}%`;
}

export function formatSigned(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return `${Number(value) >= 0 ? "+" : ""}${Number(value).toFixed(digits)}`;
}

export function formatWhole(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return String(Math.round(Number(value)));
}

export function teamLabel(team) {
  return team?.name ? `${team.abbr} • ${team.name}` : "Select team";
}

export function buildGameDetailTitle(game) {
  if (!game) {
    return "";
  }
  return `${game.displayAwayTeam} at ${game.displayHomeTeam} • Week ${game.week}, ${game.season} (${game.seasonTypeLabel})`;
}

export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export function groupBy(items, getKey) {
  return items.reduce((accumulator, item) => {
    const key = getKey(item);
    if (!accumulator[key]) {
      accumulator[key] = [];
    }
    accumulator[key].push(item);
    return accumulator;
  }, {});
}
