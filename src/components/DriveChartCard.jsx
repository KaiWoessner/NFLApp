import { useId } from "react";

const RESULT_COLORS = {
  TOUCHDOWN: "orange",
  FIELD_GOAL: "gold",
  PUNT: "brown",
  INTERCEPTION: "blue",
  FUMBLE: "blue",
  DOWNS: "purple",
};

function driveBarGeometry(row, team1) {
  const yStart = Number(row.yardlineStart);
  const yEnd = Number(row.yardlineEnd);
  const qmod = Number(row.qtr) % 2;
  const offenseTeam = row.posteam;

  let left;
  let width;

  if (qmod !== 0) {
    if (offenseTeam === team1) {
      left = yStart;
      width = yEnd - yStart;
    } else {
      left = 100 - yStart;
      width = yStart - yEnd;
    }
  } else if (offenseTeam === team1) {
    left = 100 - yStart;
    width = yStart - yEnd;
  } else {
    left = yStart;
    width = yEnd - yStart;
  }

  return {
    startX: left,
    endX: left + width,
    width,
  };
}

function LegendSwatches({ title, items }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">{title}</p>
      <div className="mt-2 flex flex-wrap gap-3">
        {items.map((item) => (
          <span key={item.label} className="inline-flex items-center gap-2 text-sm text-slate-700">
            <span
              className="inline-block h-3.5 w-3.5 rounded-sm border border-slate-900/10"
              style={{ background: item.color }}
            />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function DriveChartCard({
  selectedGame,
  driveSummary,
  quarterColors,
  vizTeam1,
  vizTeam2,
  teamsByAbbr,
}) {
  const width = 940;
  const leftPad = 28;
  const topPad = 24;
  const rowSpacing = 20;
  const barHeight = 13;
  const fieldWidth = 884;
  const fieldHeight = Math.max(136, driveSummary.length * rowSpacing + 6);
  const height = fieldHeight + 44;
  const scaleX = (value) => leftPad + (value / 100) * fieldWidth;
  const scaleY = (value) => topPad + value;
  const team1Color = teamsByAbbr[selectedGame.awayTeam]?.color || "#334155";
  const team2Color = teamsByAbbr[selectedGame.homeTeam]?.color || "#64748b";
  const fieldNumbers = [10, 20, 30, 40, 50, 40, 30, 20, 10];
  const quarterGroups = [];
  const fieldClipPathId = useId().replace(/:/g, "");
  const fieldBaseColor = "#d8ead1";
  const renderedQuarterColors = quarterColors;

  driveSummary.forEach((row, index) => {
    const group = quarterGroups.find((item) => item.qtr === row.qtr);
    if (group) {
      group.endIndex = index;
    } else {
      quarterGroups.push({ qtr: row.qtr, startIndex: index, endIndex: index });
    }
  });

  return (
    <section className="surface-card min-w-0 rounded-[2rem] p-4 sm:p-5">
      <div className="mb-5 grid gap-4 xl:grid-cols-[1fr_1.2fr_1.3fr_1.4fr] xl:items-start">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Final Score</p>
          <p className="mt-2 text-2xl font-black tracking-tight text-slate-900">
            <span style={{ color: teamsByAbbr[selectedGame.awayTeam]?.color || "#334155" }}>{selectedGame.awayScore}</span>
            <span className="px-1 text-slate-400">-</span>
            <span style={{ color: teamsByAbbr[selectedGame.homeTeam]?.color || "#334155" }}>{selectedGame.homeScore}</span>
          </p>
        </div>

        <LegendSwatches
          title="Matchup"
          items={[
            { label: selectedGame.awayTeam, color: team1Color },
            { label: selectedGame.homeTeam, color: team2Color },
          ]}
        />

        <LegendSwatches
          title="Quarter"
          items={renderedQuarterColors.map((color, index) => ({
            label: ["1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr", "OT Qtr"][index] || `Q${index + 1}`,
            color,
          }))}
        />

        <LegendSwatches
          title="Results"
          items={[
            { label: "Start", color: "rgb(242,242,242)" },
            { label: "Punt", color: "brown" },
            { label: "TO", color: "blue" },
            { label: "Downs", color: "purple" },
            { label: "FG", color: "gold" },
            { label: "TD", color: "orange" },
          ]}
        />
      </div>

      <div className="overflow-hidden rounded-[1.5rem] bg-[#f6f4ed] p-2 sm:p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-auto w-full">
          <defs>
            <clipPath id={fieldClipPathId}>
              <rect x={leftPad} y={topPad} width={fieldWidth} height={fieldHeight} rx="18" />
            </clipPath>
          </defs>

          <g clipPath={`url(#${fieldClipPathId})`}>
            <rect x={leftPad} y={topPad} width={fieldWidth} height={fieldHeight} rx="18" fill={fieldBaseColor} />

            {quarterGroups.map((quarter, index) => {
              const y = scaleY(quarter.startIndex * rowSpacing);
              const nextQuarter = quarterGroups[index + 1];
              const quarterHeight = nextQuarter
                ? (nextQuarter.startIndex - quarter.startIndex) * rowSpacing
                : fieldHeight - quarter.startIndex * rowSpacing;
              return (
                <rect
                  key={quarter.qtr}
                  x={leftPad}
                  y={y}
                  width={fieldWidth}
                  height={quarterHeight}
                  fill={renderedQuarterColors[index] || renderedQuarterColors[renderedQuarterColors.length - 1] || fieldBaseColor}
                />
              );
            })}

            {Array.from({ length: 9 }, (_, index) => (
              <line
                key={index}
                x1={scaleX((index + 1) * 10)}
                y1={topPad}
                x2={scaleX((index + 1) * 10)}
                y2={topPad + fieldHeight}
                stroke="#1f1f1f"
                strokeWidth="1.5"
                opacity="0.9"
              />
            ))}

            {driveSummary.map((row, index) => {
              const geometry = driveBarGeometry(row, vizTeam1);
              const barX = scaleX(Math.min(geometry.startX, geometry.endX));
              const barWidth = Math.max(4, Math.abs(scaleX(geometry.endX) - scaleX(geometry.startX)));
              const y = scaleY(index * rowSpacing + (rowSpacing - barHeight) / 2);
              const startCapX = geometry.width >= 0 ? scaleX(geometry.startX) : scaleX(geometry.startX) - 5;
              const resultColor = RESULT_COLORS[row.driveResult];
              const resultCapX = geometry.width >= 0 ? scaleX(geometry.endX) - 5 : scaleX(geometry.endX);

              return (
                <g key={`${row.drive}-${index}`}>
                  <rect
                    x={barX}
                    y={y}
                    width={barWidth}
                    height={barHeight}
                    rx="7"
                    fill={teamsByAbbr[row.posteam]?.color || "#64748b"}
                    stroke="#ffffff"
                    strokeWidth="1"
                  />
                  <rect x={startCapX} y={y} width="5" height={barHeight} rx="2" fill="rgb(242,242,242)" />
                  {resultColor ? <rect x={resultCapX} y={y} width="5" height={barHeight} rx="2" fill={resultColor} /> : null}
                </g>
              );
            })}
          </g>

          <rect
            x={leftPad}
            y={topPad}
            width={fieldWidth}
            height={fieldHeight}
            rx="18"
            fill="none"
            stroke="#5b5b5b"
            strokeWidth="1.2"
          />

          {Array.from({ length: 9 }, (_, index) => {
            const yard = (index + 1) * 10;
            return (
              <g key={`yard-${yard}`}>
                <text
                  x={scaleX(yard)}
                  y={topPad - 8}
                  textAnchor="middle"
                  className="fill-slate-800 text-[12px] font-semibold"
                >
                  {fieldNumbers[index]}
                </text>
                <text
                  x={scaleX(yard)}
                  y={topPad + fieldHeight + 18}
                  textAnchor="middle"
                  className="fill-slate-800 text-[12px] font-semibold"
                >
                  {fieldNumbers[index]}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </section>
  );
}
