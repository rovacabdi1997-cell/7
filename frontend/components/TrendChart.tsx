import type { TrendPoint } from "@/features/data/types";
import { num } from "@/features/i18n/tk";

/** Hourly output (bars) against plan (dashed line). Plain SVG, no chart library,
    so it works on a plant network with no internet. */
export function TrendChart({ points, unit, height = 220, width = 760, fontSize = 11 }: {
  points: TrendPoint[];
  unit: string;
  height?: number;
  width?: number;
  fontSize?: number;
}) {
  if (points.length === 0) {
    return <div className="flex items-center justify-center text-sm text-muted" style={{ height }}>Tendensiýa üçin maglumat ýok</div>;
  }
  const pad = { top: 16, right: 12, bottom: fontSize * 2.6, left: fontSize * 5.2 };
  const max = Math.max(1, ...points.map((p) => Math.max(p.actual ?? 0, p.plan ?? 0))) * 1.12;
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const slot = innerW / Math.max(points.length, 12);
  const barW = Math.max(4, slot * 0.62);
  const y = (v: number) => pad.top + innerH - (v / max) * innerH;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => t * max);
  const plan = points.find((p) => p.plan !== null)?.plan ?? null;
  const labelEvery = points.length > 16 ? 3 : points.length > 8 ? 2 : 1;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-auto w-full" role="img" aria-label={`Sagatlaýyn önümçilik, ${unit}`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={pad.left} x2={width - pad.right} y1={y(t)} y2={y(t)} stroke="var(--color-line)" />
          <text x={pad.left - 8} y={y(t) + fontSize / 3} textAnchor="end" fontSize={fontSize} fill="var(--color-muted)" className="tabular">
            {num(t)}
          </text>
        </g>
      ))}
      {points.map((p, i) => {
        const x = pad.left + i * slot + (slot - barW) / 2;
        const v = p.actual ?? 0;
        const below = plan !== null && v < plan * 0.8;
        return (
          <g key={p.hour}>
            <rect x={x} y={y(v)} width={barW} height={Math.max(0, pad.top + innerH - y(v))} rx="2"
              fill={below ? "var(--color-brand-200)" : "var(--color-brand-600)"}>
              <title>{`${p.hour}: ${num(v, 1)} ${unit}`}</title>
            </rect>
            {i % labelEvery === 0 && (
              <text x={x + barW / 2} y={height - fontSize * 0.7} textAnchor="middle" fontSize={fontSize} fill="var(--color-muted)" className="tabular">
                {p.hour}
              </text>
            )}
          </g>
        );
      })}
      {plan !== null && (
        <line x1={pad.left} x2={width - pad.right} y1={y(plan)} y2={y(plan)}
          stroke="var(--color-ink)" strokeWidth="1.5" strokeDasharray="6 5" />
      )}
    </svg>
  );
}

export function TrendLegend({ unit }: { unit: string }) {
  return (
    <div className="flex items-center gap-4 text-xs text-muted">
      <span className="flex items-center gap-1.5"><span className="inline-block h-2.5 w-2.5 rounded-sm bg-brand-600" />Hakyky ({unit}/sag)</span>
      <span className="flex items-center gap-1.5"><span className="inline-block w-4 border-t-2 border-dashed border-ink" />Meýilnama</span>
    </div>
  );
}
