import { groupBy } from "../lib/utils";

function buildLinePath(points, scaleX, scaleY) {
  return points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${scaleX(point.weekIndex)} ${scaleY(point.rank)}`)
    .join(" ");
}

function pickLogoWeeks(weekLabels) {
  const uniqueWeeks = weekLabels.map((label) => label.weekIndex);
  const targetColumns = Math.min(5, uniqueWeeks.length);
  if (targetColumns <= 1) {
    return uniqueWeeks.length ? [uniqueWeeks[uniqueWeeks.length - 1]] : [];
  }

  const selected = [];
  for (let index = 0; index < targetColumns; index += 1) {
    const position = Math.round((index * (uniqueWeeks.length - 1)) / (targetColumns - 1));
    selected.push(uniqueWeeks[position]);
  }

  return [...new Set(selected)];
}

export default function RankingsChart({ title, subtitle, data, weekLabels, teamsByAbbr }) {
  if (!data?.length) {
    return (
      <section className="surface-card rounded-[2rem] p-5">
        <p className="text-sm text-slate-600">Ranking data was not available for this season.</p>
      </section>
    );
  }

  const width = 1040;
  const height = 650;
  const padding = { top: 52, right: 88, bottom: 76, left: 44 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const grouped = groupBy(data, (item) => item.team);
  const selectedWeeks = pickLogoWeeks(weekLabels);
  const scaleX = (weekIndex) =>
    padding.left +
    ((weekIndex - 1) / Math.max(1, weekLabels.length - 1)) * plotWidth;
  const scaleY = (rank) => padding.top + ((rank - 1) / 31) * plotHeight;
  const sampledTicks =
    weekLabels.length <= 18
      ? weekLabels
      : weekLabels.filter((_, index) => index % Math.max(1, Math.floor(weekLabels.length / 8)) === 0);

  return (
    <section className="surface-card rounded-[2rem] p-5">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{subtitle}</p>
        <h3 className="mt-2 text-xl font-semibold text-slate-900">{title}</h3>
      </div>

      <div className="overflow-x-auto rounded-[1.5rem] border border-slate-900/8 bg-white p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="min-w-[820px]">
          <rect
            x={padding.left}
            y={padding.top}
            width={plotWidth}
            height={plotHeight}
            rx="22"
            fill="#f8f8f6"
          />

          {Array.from({ length: 8 }, (_, index) => {
            const rank = 1 + index * 4;
            return (
              <line
                key={rank}
                x1={padding.left}
                y1={scaleY(rank)}
                x2={padding.left + plotWidth}
                y2={scaleY(rank)}
                stroke="#d4d4d4"
                strokeWidth="1"
              />
            );
          })}

          {weekLabels.map((label) => (
            <line
              key={label.weekIndex}
              x1={scaleX(label.weekIndex)}
              y1={padding.top}
              x2={scaleX(label.weekIndex)}
              y2={padding.top + plotHeight}
              stroke="#d9d9d9"
              strokeWidth="1"
              opacity="0.6"
            />
          ))}

          {Object.entries(grouped).map(([team, points]) => (
            <path
              key={team}
              d={buildLinePath(points, scaleX, scaleY)}
              fill="none"
              stroke={teamsByAbbr[team]?.color || "#64748b"}
              strokeWidth="1.35"
              opacity="0.6"
            />
          ))}

          {data
            .filter((row) => selectedWeeks.includes(row.weekIndex))
            .map((row) => {
              const x = scaleX(row.weekIndex) - 12;
              const y = scaleY(row.rank) - 12;
              const team = teamsByAbbr[row.team];
              return team?.logoUrl ? (
                <image key={`${row.team}-${row.weekIndex}`} href={team.logoUrl} x={x} y={y} width="24" height="24" />
              ) : (
                <text
                  key={`${row.team}-${row.weekIndex}`}
                  x={scaleX(row.weekIndex)}
                  y={scaleY(row.rank) + 4}
                  textAnchor="middle"
                  className="fill-slate-900 text-[9px] font-bold"
                >
                  {row.team}
                </text>
              );
            })}

          <line
            x1={padding.left + plotWidth + 36}
            y1={padding.top + plotHeight - 4}
            x2={padding.left + plotWidth + 36}
            y2={padding.top + 4}
            stroke="#111827"
            strokeWidth="2"
          />
          <path
            d={`M ${padding.left + plotWidth + 31} ${padding.top + 10} L ${padding.left + plotWidth + 36} ${padding.top + 2} L ${padding.left + plotWidth + 41} ${padding.top + 10}`}
            fill="none"
            stroke="#111827"
            strokeWidth="2"
          />
          <text x={padding.left + plotWidth + 36} y={padding.top - 8} textAnchor="middle" className="fill-slate-900 text-[11px] font-bold">
            Best
          </text>
          <text
            x={padding.left + plotWidth + 36}
            y={padding.top + plotHeight + 20}
            textAnchor="middle"
            className="fill-slate-900 text-[11px] font-bold"
          >
            Worst
          </text>

          {sampledTicks.map((label) => (
            <text
              key={`tick-${label.weekIndex}`}
              x={scaleX(label.weekIndex)}
              y={padding.top + plotHeight + 28}
              textAnchor="middle"
              className="fill-slate-700 text-[11px]"
            >
              {label.week}
            </text>
          ))}

          <text
            x={padding.left + plotWidth / 2}
            y={padding.top + plotHeight + 54}
            textAnchor="middle"
            className="fill-slate-900 text-[12px] font-semibold"
          >
            Week
          </text>
        </svg>
      </div>
    </section>
  );
}
