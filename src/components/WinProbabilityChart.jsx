function scalePoint(point, width, height, padding) {
  return {
    x: padding.left + (point.x / 200) * width,
    y: padding.top + ((100 - point.homeWp) / 100) * height,
  };
}

function buildPolygons(points) {
  const baseline = 50;
  const polygons = [];

  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    const startAbove = start.homeWp >= baseline;
    const endAbove = end.homeWp >= baseline;

    if (startAbove === endAbove) {
      polygons.push({
        colorKey: startAbove ? "home" : "away",
        points: [
          [start.x, baseline],
          [start.x, start.homeWp],
          [end.x, end.homeWp],
          [end.x, baseline],
        ],
      });
      continue;
    }

    const t = (baseline - start.homeWp) / (end.homeWp - start.homeWp);
    const crossX = start.x + (end.x - start.x) * t;

    polygons.push({
      colorKey: startAbove ? "home" : "away",
      points: [
        [start.x, baseline],
        [start.x, start.homeWp],
        [crossX, baseline],
      ],
    });
    polygons.push({
      colorKey: endAbove ? "home" : "away",
      points: [
        [crossX, baseline],
        [end.x, end.homeWp],
        [end.x, baseline],
      ],
    });
  }

  return polygons;
}

function leftRoundedRectPath(x, y, width, height, radius) {
  const cappedRadius = Math.min(radius, height / 2, width);
  return [
    `M ${x + cappedRadius} ${y}`,
    `H ${x + width}`,
    `V ${y + height}`,
    `H ${x + cappedRadius}`,
    `Q ${x} ${y + height} ${x} ${y + height - cappedRadius}`,
    `V ${y + cappedRadius}`,
    `Q ${x} ${y} ${x + cappedRadius} ${y}`,
    "Z",
  ].join(" ");
}

export default function WinProbabilityChart({ selectedGame, winProbability, teamsByAbbr }) {
  const points = winProbability?.points || [];
  const width = 920;
  const height = 300;
  const padding = { top: 28, right: 70, bottom: 28, left: 24 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const homeColor = teamsByAbbr[selectedGame.homeTeam]?.color || "#475569";
  const awayColor = teamsByAbbr[selectedGame.awayTeam]?.color || "#64748b";
  const scaledPoints = points.map((point) => scalePoint(point, plotWidth, plotHeight, padding));
  const polygons = buildPolygons(points);
  const plotFramePath = leftRoundedRectPath(padding.left, padding.top, plotWidth, plotHeight, 20);
  const linePath = scaledPoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  if (!points.length) {
    return (
      <section className="surface-card rounded-[2rem] p-5">
        <p className="text-sm text-slate-600">Win probability data was not available for this game.</p>
      </section>
    );
  }

  return (
    <section className="surface-card min-w-0 rounded-[2rem] p-4 sm:p-5">
      <div className="mb-4">
        <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Win Probability</p>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">Game flow by play</h3>
      </div>

      <div className="overflow-hidden rounded-[1.5rem] bg-[#f6f4ed] p-2 sm:p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-auto w-full">
          <path d={plotFramePath} fill="#f6f4ed" stroke="#111827" strokeWidth="1.2" />

          {[50, 60, 70, 80, 90].flatMap((value) => {
            const mirrored = value === 50 ? [50] : [value, 100 - value];
            return mirrored.map((lineValue) => (
              <line
                key={`guide-${value}-${lineValue}`}
                x1={padding.left}
                y1={padding.top + ((100 - lineValue) / 100) * plotHeight}
                x2={padding.left + plotWidth}
                y2={padding.top + ((100 - lineValue) / 100) * plotHeight}
                stroke="#111827"
                strokeWidth="0.8"
                opacity="0.14"
              />
            ));
          })}

          {polygons.map((polygon, index) => (
            <polygon
              key={`${polygon.colorKey}-${index}`}
              points={polygon.points
                .map(([x, y]) => {
                  const scaled = scalePoint({ x, homeWp: y }, plotWidth, plotHeight, padding);
                  return `${scaled.x},${scaled.y}`;
                })
                .join(" ")}
              fill={polygon.colorKey === "home" ? homeColor : awayColor}
              opacity="0.5"
            />
          ))}

          <line
            x1={padding.left}
            y1={padding.top + plotHeight / 2}
            x2={padding.left + plotWidth}
            y2={padding.top + plotHeight / 2}
            stroke="#111827"
            strokeWidth="1.2"
          />

          {winProbability.quarters?.map((quarter, index) => {
            if (index === winProbability.quarters.length - 1) {
              return null;
            }

            const x = padding.left + (quarter.end / 200) * plotWidth;
            return <line key={quarter.label} x1={x} y1={padding.top} x2={x} y2={padding.top + plotHeight} stroke="#111827" strokeWidth="1" />;
          })}

          <path d={linePath} fill="none" stroke="#111827" strokeWidth="2" />

          {winProbability.quarters?.map((quarter) => {
            const center = padding.left + (((quarter.start + quarter.end) / 2) / 200) * plotWidth;
            return (
              <text
                key={quarter.label}
                x={center}
                y={padding.top + 18}
                textAnchor="middle"
                className="fill-slate-900 text-[11px] font-bold"
              >
                {quarter.label}
              </text>
            );
          })}

          {Array.from({ length: 19 }, (_, index) => (index + 1) * 10).map((play) => {
            const x = padding.left + (play / 200) * plotWidth;
            return (
              <g key={`play-tick-${play}`}>
                <line
                  x1={x}
                  y1={padding.top + plotHeight}
                  x2={x}
                  y2={padding.top + plotHeight + 8}
                  stroke="#111827"
                  strokeWidth="1"
                  opacity="0.55"
                />
                <text
                  x={x}
                  y={padding.top + plotHeight + 20}
                  textAnchor="middle"
                  className="fill-slate-700 text-[10px] font-semibold"
                >
                  {play}
                </text>
              </g>
            );
          })}

          {[100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0].map((value) => (
            <g key={value}>
              <text
                x={padding.left + plotWidth + 14}
                y={padding.top + ((100 - value) / 100) * plotHeight + 4}
                className="fill-slate-700 text-[13px] font-bold"
              >
                {value >= 50 ? value : 100 - value}
              </text>
            </g>
          ))}

          <text
            x={padding.left + 18}
            y={padding.top + 22}
            className="text-[22px] font-black"
            style={{ fill: homeColor }}
          >
            {selectedGame.displayHomeTeam}
          </text>
          <text
            x={padding.left + 18}
            y={padding.top + plotHeight - 14}
            className="text-[22px] font-black"
            style={{ fill: awayColor }}
          >
            {selectedGame.displayAwayTeam}
          </text>
        </svg>
      </div>
    </section>
  );
}
