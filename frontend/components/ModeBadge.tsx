import type { DataMode } from "@/features/data/types";
import { MODE } from "@/features/i18n/tk";

const TONE: Record<DataMode, string> = {
  "SIMULÝASIÝA": "bg-amber-100 text-amber-900 ring-amber-300",
  HAKYKY: "bg-emerald-50 text-emerald-800 ring-emerald-300",
  "ÝOK": "bg-slate-100 text-slate-600 ring-slate-300",
};

export function ModeBadge({ mode, size = "md" }: { mode: DataMode; size?: "sm" | "md" }) {
  const pad = size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";
  return (
    <span className={`inline-flex items-center rounded font-semibold tracking-wide ring-1 ${pad} ${TONE[mode]}`}>
      {MODE[mode]}
    </span>
  );
}
