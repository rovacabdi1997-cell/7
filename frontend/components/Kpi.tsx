import type { Metric } from "@/features/data/types";
import { num } from "@/features/i18n/tk";
import { ModeBadge } from "./ModeBadge";

/** One labelled value. Shows "—" when the source has no value. */
export function Kpi({ label, metric, decimals = 0, unit, hint, emphasis = false }: {
  label: string;
  metric: Metric | null | undefined;
  decimals?: number;
  unit?: string;
  hint?: string;
  emphasis?: boolean;
}) {
  const value = metric?.value ?? null;
  return (
    <div className="min-w-0">
      <div className="flex items-center justify-between gap-2">
        <span className="truncate text-sm text-muted">{label}</span>
        {metric && metric.mode !== "HAKYKY" && <ModeBadge mode={metric.mode} size="sm" />}
      </div>
      <div className={`tabular mt-1 font-semibold text-ink ${emphasis ? "text-4xl" : "text-2xl"}`}>
        {num(value, decimals)}
        <span className="ml-1.5 text-base font-medium text-muted">{unit ?? metric?.unit}</span>
      </div>
      {hint && <div className="mt-0.5 text-xs text-muted">{hint}</div>}
    </div>
  );
}

export function Progress({ pct }: { pct: number | null | undefined }) {
  const width = Math.max(0, Math.min(100, pct ?? 0));
  const tone = pct === null || pct === undefined ? "bg-idle" : pct >= 95 ? "bg-ok" : pct >= 80 ? "bg-brand-600" : "bg-warn";
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-brand-50" role="progressbar" aria-valuenow={pct ?? undefined} aria-valuemin={0} aria-valuemax={100}>
      <div className={`h-full rounded-full ${tone}`} style={{ width: `${width}%` }} />
    </div>
  );
}
